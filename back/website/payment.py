from datetime import datetime, timedelta
from flask import Blueprint, Flask, jsonify, render_template, request
from flask_login import login_required, current_user
import requests
from .models import Assinaturas
from .json_responses import successful_response, error_response
from .payment_api import create_payment_eternal, create_payment_anual, create_payment_monthly

payment = Blueprint('payment', __name__)

@payment.route('/payment_checkout')
@login_required
def payment_checkout(): 
    link_mensal = create_payment_monthly()
    link_anual  = create_payment_anual()
    link_eterno = create_payment_eternal()
    try:
        request.form.get('choosen_preference')
        return successful_response(
            description="Successfully generated the payment preferences and choosen preference",
            data=jsonify({"link_anual": link_anual, "link_mensal": link_mensal, "link_eterno": link_eterno}))
    
    except Exception as e:
        return error_response(
            description="Could not get choosen preference. Perhaps you forgot to choose the payment type?",
            error_details={"exception": e}
        )

 
@payment.route('/payment_done')
@login_required
def payment_done():
    try:
        user_id = current_user.get_id()
        assinatura = Assinaturas(user_id=user_id, inicio = datetime.now(), fim = datetime.now()+timedelta(days=31), TipoAssinatura = 0)

        return "<h1>Compra concluída!</h1>"

    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Não foi possível localizar o usuário...</h1>'
        return hed + error_text

@payment.route('/payment_denied')
def payment_denied():
    return "<h1>Compra negada!</h1>"