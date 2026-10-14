from flask import Flask, render_template, jsonify, request
import sqlite3
import os
import time

app = Flask(__name__)

DB_FILE = "shopshield.db"

# 1. Database Setup Function
def init_db():
    """Creates the SQLite database file and tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create an orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            timestamp REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database immediately when backend starts
init_db()

# Mock list of products for the frontend layout
PRODUCTS = [
    {"id": 1, "name": "Firewall Core Shield", "price": 49.99},
    {"id": 2, "name": "Encrypted Data Vault", "price": 99.99},
    {"id": 3, "name": "Proxy Router Pro", "price": 29.99}
]

@app.route('/')
def home():
    return render_template('shop.html', products=PRODUCTS)

# 2. Day 2 Task: The Order API Route
@app.route('/api/order', methods=['POST'])
def place_order():
    """Receives an order request and saves it securely to SQLite."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON data"}), 400
            
        product_id = data.get('product_id')
        
        # Find the product info from our list matching the ID sent
        product = next((p for p in PRODUCTS if p["id"] == product_id), None)
        
        if not product:
            return jsonify({"success": False, "error": "Product not found"}), 404
            
        # Save order details into SQLite
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (product_id, product_name, price, timestamp) VALUES (?, ?, ?, ?)",
            (product["id"], product["name"], product["price"], time.time())
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Successfully purchased {product['name']}! Saved to database."
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
