# Nahome Kifle
# Product Service

import os
from flask import Flask, jsonify, request
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Connect to Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/products', methods=['GET'])
def get_all_products():
    """Fetch all products."""
    response = supabase.table('products').select('*').execute()
    return jsonify({"products": response.data})

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Fetch a single product by ID."""
    response = supabase.table('products').select('*').eq('id', product_id).execute()
    if not response.data:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"product": response.data[0]})

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product_quantity(product_id):
    """Update the quantity of a product."""
    data = request.json
    new_quantity = data.get("quantity")
    if new_quantity is None:
        return jsonify({"error": "Invalid request"}), 400

    response = supabase.table('products').update({"quantity": new_quantity}).eq('id', product_id).execute()
    if not response.data:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"message": "Product updated successfully", "product": response.data[0]})

if __name__ == '__main__':
    app.run(port=5000, debug=True)