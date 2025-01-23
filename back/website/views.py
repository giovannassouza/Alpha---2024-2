from flask import Blueprint, render_template
from flask_login import current_user#, login_required

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html", user=current_user)

@views.route('/auth-test')
def auth_test():
    return render_template("auth-test.html")