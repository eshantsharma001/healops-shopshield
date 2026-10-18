import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure Database & Upload Settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join('static', 'uploads')
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

# Combined Storefront Route: Handles Category Filtering + Search
@app.route('/')
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
    
    # Get a list of all unique categories in the database to display in the filter bar
    # (Clean list comprehension filters out duplicates dynamically)
    categories = [p.category for p in Product.query.with_entities(Product.category).distinct()]
    
    return render_template('shop.html', products=all_products, categories=categories)

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

with app.app_context():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
