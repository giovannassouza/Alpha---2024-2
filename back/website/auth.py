from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return "<p>Login</p>"

@auth.route('/sign-up')
def sign_up():
    return "<p>SignUp</p>"