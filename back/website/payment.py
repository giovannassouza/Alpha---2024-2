from flask import Blueprint, Flask, render_template
from flask_login import login_required
import requests
from .payment_api import create_payment_eternal, create_payment_anual, create_payment_monthly

payment = Blueprint('payment', __name__)

@payment.route('/payment_checkout')
# @login_required
def payment_checkout(): 
    """
    Página de checkout de pagamento
    ---
    tags:
      - Pagamentos
    responses:
      200:
        description: Página com os links de pagamento
        content:
          text/html:
            example: "<html>...</html>"
    """
    link_mensal = create_payment_monthly()
    link_anual  = create_payment_anual()
    link_eterno = create_payment_eternal()
    return render_template("payment.html", link_anual=link_anual, link_mensal=link_mensal, link_eterno=link_eterno)

 
@payment.route('/payment_done')
def payment_done():
    return "<h1>Compra concluída!</h1>"


@payment.route('/payment_denied')
def payment_denied():
    return "<h1>Compra negada!</h1>"