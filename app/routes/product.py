# Nahome Kifle
# Product Service

import os
from flask import Blueprint, jsonify, request, session
from supabase import create_client, Client
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

# Create blueprint
product_blueprint = Blueprint('product', __name__)

# Connect to Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Please log in to access this feature"}), 401
        return f(*args, **kwargs)
    return decorated_function

@product_blueprint.route('/', methods=['GET'])
@login_required
def get_products():
    """Get all available products."""
    try:
        response = supabase.table('products')\
            .select('*')\
            .execute()
            
        return jsonify({"products": response.data}), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch products"}), 500

@product_blueprint.route('/<int:product_id>', methods=['GET'])
@login_required
def get_product(product_id):
    """Get a specific product by ID."""
    try:
        response = supabase.table('products')\
            .select('*')\
            .eq('id', product_id)\
            .execute()
            
        if not response.data:
            return jsonify({"error": "Product not found"}), 404
            
        return jsonify({"product": response.data[0]}), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch product"}), 500

@product_blueprint.route('/<int:product_id>', methods=['PUT'])
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