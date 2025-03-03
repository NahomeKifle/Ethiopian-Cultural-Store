from flask import Blueprint, render_template
from functools import wraps
from flask import session, redirect, url_for

views_blueprint = Blueprint('views', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@views_blueprint.route('/')
def index():
    return render_template('base.html')

@views_blueprint.route('/signup')
def signup():
    return render_template('sign_up.html')

@views_blueprint.route('/login')
def login():
    return render_template('log_in.html')

@views_blueprint.route('/products')
@login_required
def products():
    return render_template('products.html') 