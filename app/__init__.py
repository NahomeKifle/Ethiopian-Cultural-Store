#Nahome Kifle
#Innit file

from flask import Flask
from .routes.cart import cart_blueprint
from .routes.product import product_blueprint
from .routes.auth import auth_blueprint  # Import the new auth blueprint

def create_app():
    app = Flask(__name__)

    # Register blueprints for cart, product, and auth
    app.register_blueprint(cart_blueprint, url_prefix='/cart')
    app.register_blueprint(product_blueprint, url_prefix='/product')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app