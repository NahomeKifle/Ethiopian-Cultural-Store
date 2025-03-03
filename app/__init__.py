#Nahome Kifle
#Init file

import os
from flask import Flask
from flask_cors import CORS
from .routes.cart import cart_blueprint
from .routes.product import product_blueprint
from .routes.auth import auth_blueprint
from .routes.views import views_blueprint

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24).hex())
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
    
    # Register blueprints
    app.register_blueprint(views_blueprint)  # No URL prefix for views
    app.register_blueprint(cart_blueprint, url_prefix='/api/cart')
    app.register_blueprint(product_blueprint, url_prefix='/api/products')
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')

    return app