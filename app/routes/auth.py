#Nahome Kifle
#Auth py file

import os
from flask import Blueprint, jsonify, request, session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

# Create Flask Blueprint for authentication
auth_blueprint = Blueprint('auth', __name__)

# Supabase connection details (consider putting these in your .env file)
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

@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('sign_up.html')
    
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Validate input
        if not all([username, email, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400

        # Check if username or email already exists
        existing_user = supabase.table('users')\
            .select('*')\
            .or_(f"username.eq.{username},email.eq.{email}")\
            .execute()
            
        if existing_user.data:
            return jsonify({'error': 'Username or email already exists'}), 400

        # Hash password and create user
        password_hash = generate_password_hash(password)
        
        new_user = {
            'username': username,
            'email': email,
            'password_hash': password_hash
        }
        
        response = supabase.table('users').insert(new_user).execute()
        
        if not response.data:
            return jsonify({'error': 'Failed to create user'}), 500
            
        return jsonify({'message': 'User created successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to create user'}), 500

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('log_in.html')
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            return jsonify({'error': 'Username and password are required'}), 400

        # Get user by username
        response = supabase.table('users')\
            .select('*')\
            .eq('username', username)\
            .execute()
        
        if not response.data:
            return jsonify({'error': 'Invalid username or password'}), 401

        user = response.data[0]
        
        # Verify password
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid username or password'}), 401

        # Update last login time
        supabase.table('users')\
            .update({'last_login': 'now()'}).eq('id', user['id'])\
            .execute()

        # Set session
        session['user_id'] = user['id']
        session['username'] = user['username']

        return jsonify({
            'message': 'Login successful',
            'redirect': '/products',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

@auth_blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_blueprint.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user's details"""
    try:
        response = supabase.table('users')\
            .select('id, username, email, created_at, last_login')\
            .eq('id', session['user_id'])\
            .execute()
            
        if not response.data:
            session.clear()
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({'user': response.data[0]}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user details'}), 500