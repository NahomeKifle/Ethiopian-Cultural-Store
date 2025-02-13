# Nahome Kifle
# Cart Service

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

@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    """Fetch all items in a user's cart."""
    response = supabase.table('cart').select('*').eq('user_id', user_id).execute()
    return jsonify({"cart": response.data})

@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_product(user_id, product_id):
    """Add a product to the user's cart."""
    # Fetch the product details
    product_response = supabase.table('products').select('*').eq('id', product_id).execute()
    if not product_response.data:
        return jsonify({"error": "Product not found"}), 404
    
    product = product_response.data[0]
    available_quantity = product['quantity']

    # Get the requested quantity
    data = request.json
    quantity_to_add = data.get('quantity', 1)

    if available_quantity < quantity_to_add:
        return jsonify({"error": "Insufficient quantity"}), 400

    # Check if the item already exists in the cart
    existing_item_response = supabase.table('cart').select('*').eq('user_id', user_id).eq('product_id', product_id).execute()
    if existing_item_response.data:
        # Update quantity
        existing_item = existing_item_response.data[0]
        new_quantity = existing_item['quantity'] + quantity_to_add
        supabase.table('cart').update({"quantity": new_quantity}).eq('id', existing_item['id']).execute()
    else:
        # Add new item to cart
        new_cart_item = {
            "user_id": user_id,
            "product_id": product_id,
            "name": product['name'],
            "price": product['price'],
            "quantity": quantity_to_add
        }
        supabase.table('cart').insert(new_cart_item).execute()

    # Update product quantity
    updated_quantity = available_quantity - quantity_to_add
    supabase.table('products').update({"quantity": updated_quantity}).eq('id', product_id).execute()

    return jsonify({"message": "Product added to cart", "product": product, "quantity_added": quantity_to_add}), 201

@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_product(user_id, product_id):
    """Remove a product from the user's cart."""
    data = request.json
    quantity_to_remove = data.get('quantity', 1)

    # Fetch the cart item
    cart_response = supabase.table('cart').select('*').eq('user_id', user_id).eq('product_id', product_id).execute()
    if not cart_response.data:
        return jsonify({"error": "Product not in cart"}), 404

    cart_item = cart_response.data[0]

    if cart_item['quantity'] < quantity_to_remove:
        return jsonify({"error": "Quantity to remove exceeds quantity in cart"}), 400

    # Update cart or remove item
    new_quantity = cart_item['quantity'] - quantity_to_remove
    if new_quantity == 0:
        supabase.table('cart').delete().eq('id', cart_item['id']).execute()
    else:
        supabase.table('cart').update({"quantity": new_quantity}).eq('id', cart_item['id']).execute()

    # Update product quantity
    product_response = supabase.table('products').select('*').eq('id', product_id).execute()
    if not product_response.data:
        return jsonify({"error": "Product not found"}), 404

    product = product_response.data[0]
    updated_quantity = product['quantity'] + quantity_to_remove
    supabase.table('products').update({"quantity": updated_quantity}).eq('id', product_id).execute()

    return jsonify({"message": "Product removed from cart", "updated_quantity_in_inventory": updated_quantity}), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)
