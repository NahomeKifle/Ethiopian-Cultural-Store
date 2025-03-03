# Nahome Kifle
# Cart Service

import os
from flask import Blueprint, jsonify, request, session
from supabase import create_client, Client
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

# Create blueprint
cart_blueprint = Blueprint('cart', __name__)

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

@cart_blueprint.route('/my-cart', methods=['GET'])
@login_required
def get_cart():
    """Fetch all items in the user's cart with product details."""
    try:
        # First get cart items
        cart_response = supabase.table('cart')\
            .select('*')\
            .eq('user_id', session['user_id'])\
            .execute()

        if not cart_response.data:
            return jsonify({"cart": [], "total": 0}), 200

        # Get product details for cart items
        cart_items = []
        total_price = 0

        for cart_item in cart_response.data:
            product_response = supabase.table('products')\
                .select('*')\
                .eq('id', cart_item['product_id'])\
                .execute()

            if product_response.data:
                product = product_response.data[0]
                item_total = float(product['price']) * cart_item['quantity']
                total_price += item_total

                cart_items.append({
                    "cart_id": cart_item['id'],
                    "product_id": product['id'],
                    "name": product['name'],
                    "price": float(product['price']),
                    "quantity": cart_item['quantity'],
                    "item_total": item_total
                })

        return jsonify({
            "cart": cart_items,
            "total": round(total_price, 2)
        }), 200

    except Exception as e:
        print(f"Error in get_cart: {str(e)}")
        return jsonify({"error": "Failed to fetch cart items"}), 500

@cart_blueprint.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_product(product_id):
    """Add a product to the user's cart."""
    try:
        data = request.json
        quantity_to_add = int(data.get('quantity', 1))

        if quantity_to_add <= 0:
            return jsonify({"error": "Quantity must be positive"}), 400

        # Check product exists and has sufficient quantity
        product_response = supabase.table('products')\
            .select('*')\
            .eq('id', product_id)\
            .execute()

        if not product_response.data:
            return jsonify({"error": "Product not found"}), 404

        product = product_response.data[0]
        if product['quantity'] < quantity_to_add:
            return jsonify({"error": "Insufficient stock"}), 400

        # Check if product already in cart
        cart_response = supabase.table('cart')\
            .select('*')\
            .eq('user_id', session['user_id'])\
            .eq('product_id', product_id)\
            .execute()

        if cart_response.data:
            # Update existing cart item
            cart_item = cart_response.data[0]
            new_quantity = cart_item['quantity'] + quantity_to_add
            
            supabase.table('cart')\
                .update({'quantity': new_quantity})\
                .eq('id', cart_item['id'])\
                .execute()
        else:
            # Add new cart item
            supabase.table('cart')\
                .insert({
                    'user_id': session['user_id'],
                    'product_id': product_id,
                    'quantity': quantity_to_add
                })\
                .execute()

        # Update product quantity
        new_stock = product['quantity'] - quantity_to_add
        supabase.table('products')\
            .update({'quantity': new_stock})\
            .eq('id', product_id)\
            .execute()

        return jsonify({
            "message": "Product added to cart",
            "quantity_added": quantity_to_add
        }), 201

    except Exception as e:
        print(f"Error in add_product: {str(e)}")
        return jsonify({"error": "Failed to add item to cart"}), 500

@cart_blueprint.route('/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_product(product_id):
    """Remove a product from the user's cart."""
    try:
        data = request.json
        quantity_to_remove = int(data.get('quantity', 1))

        if quantity_to_remove <= 0:
            return jsonify({"error": "Quantity must be positive"}), 400

        # Get cart item
        cart_response = supabase.table('cart')\
            .select('*')\
            .eq('user_id', session['user_id'])\
            .eq('product_id', product_id)\
            .execute()

        if not cart_response.data:
            return jsonify({"error": "Product not in cart"}), 404

        cart_item = cart_response.data[0]
        if cart_item['quantity'] < quantity_to_remove:
            return jsonify({"error": "Cannot remove more items than in cart"}), 400

        # Get product to update stock
        product_response = supabase.table('products')\
            .select('*')\
            .eq('id', product_id)\
            .execute()

        if not product_response.data:
            return jsonify({"error": "Product not found"}), 404

        product = product_response.data[0]

        # Update cart
        new_quantity = cart_item['quantity'] - quantity_to_remove
        if new_quantity == 0:
            supabase.table('cart')\
                .delete()\
                .eq('id', cart_item['id'])\
                .execute()
        else:
            supabase.table('cart')\
                .update({'quantity': new_quantity})\
                .eq('id', cart_item['id'])\
                .execute()

        # Update product stock
        new_stock = product['quantity'] + quantity_to_remove
        supabase.table('products')\
            .update({'quantity': new_stock})\
            .eq('id', product_id)\
            .execute()

        return jsonify({
            "message": "Product removed from cart",
            "quantity_removed": quantity_to_remove
        }), 200

    except Exception as e:
        print(f"Error in remove_product: {str(e)}")
        return jsonify({"error": "Failed to remove item from cart"}), 500
