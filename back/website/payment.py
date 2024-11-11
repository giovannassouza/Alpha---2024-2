from flask import Blueprint
from flask_login import login_required
import requests

payment = Blueprint('payment', __name__)

@payment.route('/payment', methods=['GET', 'POST'])
# @login_required
def payment_checkout(): 
    return "<h1>Payment checkout</h1>"