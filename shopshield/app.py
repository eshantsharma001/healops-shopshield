import sys
import io
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from rate_limiter import is_request_allowed, get_rate_limiter_metrics
from inventory_client import fetch_stock_with_retry, decrement_stock_batch
import os
import json
import re
import secrets
import uuid
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = os.environ.get("SHOPSHIELD_SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure Database & Upload Settings
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SHOPSHIELD_DATABASE_URI", "sqlite:///shop.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

db = SQLAlchemy(app)

# Updated Database Model with Category Column
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    badge = db.Column(db.String(50), default="Shield Verified")
    category = db.Column(db.String(50), default="Uncategorized") # New field!
    image_filename = db.Column(db.String(300), default="default.jpg")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True, index=True)
    email = db.Column(db.String(254), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_code = db.Column(db.String(40), nullable=False, unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    customer_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    city_postal = db.Column(db.String(120), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    payment_reference = db.Column(db.String(12), nullable=False, default="")
    total = db.Column(db.Float, nullable=False)
    items_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def current_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


def order_payload(order):
    return {
        "order_id": order.order_code,
        "customer_name": order.customer_name,
        "address": order.address,
        "city_postal": order.city_postal,
        "payment_method": order.payment_method,
        "payment_reference": order.payment_reference,
        "total": order.total,
        "items": json.loads(order.items_json),
        "created_at": order.created_at.isoformat(),
        "delivery_estimate": (order.created_at + timedelta(days=5)).date().isoformat(),
    }


def format_inr(value):
    value = f"{float(value):.2f}"
    whole, fraction = value.split(".")
    if len(whole) > 3:
        last_group, remaining = whole[-3:], whole[:-3]
        groups = []
        while remaining:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        whole = ",".join(groups + [last_group])
    return f"₹{whole}.{fraction}"


app.jinja_env.filters["inr"] = format_inr
# Admin Security Credentials
def check_auth(username, password):
    return username == 'admin' and password == '123'

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response(
                'Access Denied: Invalid credentials.', 401,
                {'WWW-Authenticate': 'Basic realm="Admin Login Required"'}
            )
        return f(*args, **kwargs)
    return decorated
# ----------------------------------------------------
# PROBLEM 4: TRAFFIC SPIKE & LOAD SHEDDING GUARD
# ----------------------------------------------------
@app.before_request
def rate_limit_guard():
    """Protects ShopShield from sudden traffic surges."""
    # Don't rate-limit internal health checks or static images
    if request.path.startswith('/health') or request.path.startswith('/static'):
        return None

    client_ip = request.remote_addr or '127.0.0.1'
    allowed, metrics = is_request_allowed(client_ip)
    
    if not allowed:
        # Shed the load with HTTP 429
        return jsonify({
            "error": "Traffic Spike Detected",
            "message": "HealOps Load Shedder: Request dropped to protect application stability.",
            "status_code": 429,
            "metrics": metrics
        }), 429
# Combined Storefront Route: Handles Category Filtering + Search
@app.route('/')
@app.route('/shop')
def home():
    search_query = request.args.get('search')
    category_filter = request.args.get('category')
    
    # Base query for all items
    query = Product.query
    
    # Apply category filter if picked
    if category_filter:
        query = query.filter_by(category=category_filter)
        
    # Apply text search filter if used
    if search_query:
        query = query.filter(Product.name.like(f"%{search_query}%"))
        
    all_products = query.all()

    # Fetch live stock from Product Service (with retry and fallback!)
    for product in all_products:
        stock_data = fetch_stock_with_retry(product.id)
        product.live_stock = stock_data["stock"]
        product.live_status = stock_data["status"]
        product.stock_source = stock_data["source"]

    # Get a list of all unique categories in the database to display in the filter bar
    categories = [p.category for p in Product.query.with_entities(Product.category).distinct()]
    
    return render_template(
        'shop.html',
        products=all_products,
        categories=categories,
        current_user=current_user(),
        upi_id=os.environ.get("SHOPSHIELD_UPI_ID", "").strip(),
    )


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400
    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,30}", username):
        return jsonify({"error": "Username must be 3–30 characters and use letters, numbers, dots, underscores, or hyphens."}), 400
    if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({"error": "Enter a valid email address."}), 400
    if not isinstance(password, str) or len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "That username or email is already registered."}), 409
    user = User(username=username, email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "That username or email is already registered."}), 409
    session.clear()
    session["user_id"] = user.id
    return jsonify({"user": {"id": user.id, "username": user.username, "email": user.email}}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400
    identifier = str(data.get("identifier") or data.get("username") or data.get("email") or "").strip()
    password = data.get("password", "")
    user = User.query.filter(
        (User.email == identifier.lower()) | (User.username == identifier)
    ).first()
    if not user or not isinstance(password, str) or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username/email or password."}), 401
    session.clear()
    session["user_id"] = user.id
    return jsonify({"user": {"id": user.id, "username": user.username, "email": user.email}})


@app.route('/api/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({"message": "You have been signed out."})


@app.route('/api/user')
def user_profile():
    user = current_user()
    if user is None:
        return jsonify({"error": "Authentication required."}), 401
    return jsonify({"id": user.id, "username": user.username, "email": user.email})


@app.route('/api/orders')
def user_orders():
    user = current_user()
    if user is None:
        return jsonify({"error": "Sign in to view your orders."}), 401
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return jsonify({"orders": [order_payload(order) for order in orders]})


@app.route('/api/payment/upi-qr')
def upi_qr():
    merchant_upi_id = os.environ.get("SHOPSHIELD_UPI_ID", "").strip()
    if not re.fullmatch(r"[A-Za-z0-9._-]{2,100}@[A-Za-z0-9.-]{2,100}", merchant_upi_id):
        return jsonify({"error": "UPI payments are not configured. Set SHOPSHIELD_UPI_ID to the store's merchant VPA."}), 503
    try:
        amount = Decimal(request.args.get("amount", "")).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return jsonify({"error": "A valid payment amount is required."}), 400
    if not amount.is_finite() or amount <= 0 or amount > Decimal("10000000"):
        return jsonify({"error": "Payment amount is outside the supported range."}), 400
    from urllib.parse import urlencode
    import qrcode
    import qrcode.image.svg

    payment_uri = "upi://pay?" + urlencode({
        "pa": merchant_upi_id,
        "pn": "ShopShield Retail",
        "am": f"{amount:.2f}",
        "cu": "INR",
        "tn": "ShopShield purchase",
    })
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(payment_uri)
    qr.make(fit=True)
    image = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    output = io.BytesIO()
    image.save(output)
    return Response(output.getvalue(), mimetype="image/svg+xml")


@app.route('/api/orders/quote', methods=['POST'])
def order_quote():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400
    items = data.get("items")
    if not isinstance(items, list) or not items or len(items) > 50:
        return jsonify({"error": "Your cart is empty or contains too many items."}), 400
    quantities = {}
    for item in items:
        if not isinstance(item, dict):
            return jsonify({"error": "The cart contains an invalid item."}), 400
        try:
            product_id = int(item.get("id"))
            quantity = int(item.get("quantity"))
        except (TypeError, ValueError):
            return jsonify({"error": "The cart contains an invalid product or quantity."}), 400
        if product_id <= 0 or quantity <= 0 or quantity > 99:
            return jsonify({"error": "Product quantities must be between 1 and 99."}), 400
        quantities[product_id] = quantities.get(product_id, 0) + quantity
        if quantities[product_id] > 99:
            return jsonify({"error": "Product quantities must be between 1 and 99."}), 400
    quoted_items = []
    for product_id, quantity in quantities.items():
        product = db.session.get(Product, product_id)
        if product is None:
            return jsonify({"error": "A product in your cart is no longer available."}), 409
        quoted_items.append({
            "id": product.id,
            "name": product.name,
            "price": round(product.price, 2),
            "quantity": quantity,
        })
    return jsonify({
        "total": round(sum(item["price"] * item["quantity"] for item in quoted_items), 2),
        "items": quoted_items,
    })


@app.route('/api/orders', methods=['POST'])
def place_order():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400
    customer_name = str(data.get("customer_name", "")).strip()
    address = str(data.get("address", "")).strip()
    city_postal = str(data.get("city_postal", "")).strip()
    payment_method = data.get("payment_method")
    payment_reference = str(data.get("payment_reference", "")).strip()
    items = data.get("items")
    if not customer_name or len(customer_name) > 120 or not address or len(address) > 300 or not city_postal or len(city_postal) > 120:
        return jsonify({"error": "Enter a valid name, street address, city, and postal code."}), 400
    if payment_method not in ("upi", "card", "cod"):
        return jsonify({"error": "Choose a supported payment method."}), 400
    if payment_method == "card":
        return jsonify({"error": "Card and NetBanking payments require a configured payment provider."}), 503
    if payment_method == "upi" and not re.fullmatch(r"\d{12}", payment_reference):
        return jsonify({"error": "Enter a valid 12-digit UPI reference number."}), 400
    if not isinstance(items, list) or not items or len(items) > 50:
        return jsonify({"error": "Your cart is empty or contains too many items."}), 400

    quantities = {}
    for item in items:
        if not isinstance(item, dict):
            return jsonify({"error": "The cart contains an invalid item."}), 400
        try:
            product_id = int(item.get("id"))
            quantity = int(item.get("quantity"))
        except (TypeError, ValueError):
            return jsonify({"error": "The cart contains an invalid product or quantity."}), 400
        if product_id <= 0 or quantity <= 0 or quantity > 99:
            return jsonify({"error": "Product quantities must be between 1 and 99."}), 400
        quantities[product_id] = quantities.get(product_id, 0) + quantity
        if quantities[product_id] > 99:
            return jsonify({"error": "Product quantities must be between 1 and 99."}), 400

    order_items = []
    for product_id, quantity in quantities.items():
        product = db.session.get(Product, product_id)
        if product is None:
            return jsonify({"error": "A product in your cart is no longer available."}), 409
        order_items.append({
            "id": product.id,
            "name": product.name,
            "price": round(product.price, 2),
            "quantity": quantity,
        })
    total = round(sum(item["price"] * item["quantity"] for item in order_items), 2)
    expected_total = data.get("expected_total")
    if expected_total is not None:
        try:
            expected_total = Decimal(str(expected_total)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return jsonify({"error": "The checkout quote is invalid. Please refresh your cart."}), 400
        if not expected_total.is_finite() or expected_total != Decimal(str(total)):
            return jsonify({"error": "Product prices changed. Please review the updated order total."}), 409
    order = Order(
        order_code=f"SH-{uuid.uuid4().hex[:10].upper()}",
        user_id=session.get("user_id"),
        customer_name=customer_name,
        address=address,
        city_postal=city_postal,
        payment_method=payment_method,
        payment_reference=payment_reference if payment_method == "upi" else "",
        total=total,
        items_json=json.dumps(order_items),
    )
    db.session.add(order)
    db.session.commit()
    try:
        stock_updates = decrement_stock_batch([
            {"product_id": product_id, "quantity": quantity}
            for product_id, quantity in quantities.items()
        ])
    except (RuntimeError, ValueError) as error:
        db.session.delete(order)
        db.session.commit()
        return jsonify({"error": str(error)}), 409
    result = order_payload(order)
    result["stock_updates"] = stock_updates.get("items", [])
    return jsonify(result), 201
# Admin panel route updated to save chosen category
@app.route('/admin', methods=['GET', 'POST'])
@requires_auth
def admin():
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price'))
        badge = request.form.get('badge')
        category = request.form.get('category') # Grab selected category
        
        file = request.files.get('product_image')
        filename = "default.jpg"
        
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        new_product = Product(name=name, price=price, badge=badge, category=category, image_filename=filename)
        db.session.add(new_product)
        db.session.commit()
        
        return redirect(url_for('admin'))
        
    all_products = Product.query.all()
    return render_template('admin.html', products=all_products)

@app.route('/admin/delete/<int:product_id>', methods=['POST'])
@requires_auth
def delete_product(product_id):
    product_to_delete = Product.query.get_or_404(product_id)
    if product_to_delete.image_filename != "default.jpg":
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product_to_delete.image_filename))
        except OSError:
            pass
            
    db.session.delete(product_to_delete)
    db.session.commit()
    return redirect(url_for('admin'))
# ----------------------------------------------------
# HEALOPS INTEGRATION ENDPOINTS
# ----------------------------------------------------

@app.route('/health')
def health():
    """HealOps calls this to verify ShopShield is alive."""
    return jsonify({
        "status": "healthy",
        "service": "shopshield"
    }), 200

@app.route('/api/metrics')
def metrics():
    """Returns traffic and load shedding metrics for HealOps."""
    return jsonify(get_rate_limiter_metrics()), 200

@app.route('/chaos/crash', methods=['POST', 'GET'])
def chaos_crash():
    """Deliberately crashes ShopShield process to test self-healing."""
    os._exit(1)
with app.app_context():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    db.create_all()

if __name__ == '__main__':
    app.run(port=5000, debug=False)
