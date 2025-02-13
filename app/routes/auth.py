#Nahome Kifle
#Auth py file

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client
import os

# Create Flask Blueprint for authentication
auth_blueprint = Blueprint('auth', __name__)

# Supabase connection details (consider putting these in your .env file)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Route for signing up a user (create an account)
@auth_blueprint.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data['email']
    password = data['password']

    # Hash the password before storing
    hashed_password = generate_password_hash(password)

    # Save user info to the database (email and hashed password)
    response = supabase.table('users').insert({'email': email, 'password': hashed_password}).execute()

    if response.status_code != 201:
        return jsonify({'error': 'User creation failed'}), 400

    return jsonify({'message': 'User created successfully'}), 201


# Route for logging in a user (check credentials)
@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    # Retrieve user by email
    response = supabase.table('users').select('email', 'password').eq('email', email).execute()

    if len(response.data) == 0:
        return jsonify({'error': 'User not found'}), 404

    # Check if the provided password matches the stored hashed password
    stored_password = response.data[0]['password']
    if not check_password_hash(stored_password, password):
        return jsonify({'error': 'Invalid password'}), 400

    # If successful, create a session (or JWT token) to keep the user logged in (simplified here)
    # For now, we'll just send a success message
    return jsonify({'message': 'User logged in successfully'}), 200