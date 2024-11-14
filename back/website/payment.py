from flask import Blueprint
from flask_login import login_required
import requests


payment = Blueprint('payment', __name__)

@payment.route('/payment_checkout')
# @login_required
def payment_checkout(): 
    return "<h1>Realizar pagamento</h1>"


@payment.route('/payment_done')
def payment_done():
    return "<h1>Compra concluída!</h1>"


@payment.route('/payment_denied')
def payment_denied():
    return "<h1>Compra negada!</h1>"
