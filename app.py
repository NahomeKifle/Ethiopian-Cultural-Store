from flask import Flask
from products import product_blueprint

app = Flask(__name__)

# Register the product blueprint
app.register_blueprint(product_blueprint, url_prefix='/api')

if __name__ == "__main__":
    app.run(port=5001)