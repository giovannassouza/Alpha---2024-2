from datetime import datetime, timedelta
from flask import Blueprint, Flask, jsonify, render_template, request, session
from flask_login import login_required, current_user
import requests
from .models import Assinaturas
from website.models import *
from .json_responses import successful_response, error_response
from .payment_api import create_payment_eternal, create_payment_anual, create_payment_monthly

payment = Blueprint('payment', __name__)
choosen_pref = -1
@payment.route('/payment_checkout', methods= ["GET", "POST"])
@login_required
def payment_checkout(): 
    """
    Checkout signature payment.
    ---
    tags:
      - Signature
    parameters:
      - name: choosen_preference
        in: formData
        type: int
        required: true
        description: Tag with which signature client is paying for.
    responses:
      200:
        description: Successfully checked out.
        schema:
          type: object
          properties:
            link_mensal:
              type: string
              description: URL of the preference created to be paid.
            link_anual:
              type: string
              description: URL of the preference created to be paid.
            link_eterno:
              type: string
              description: URL of the preference created to be paid.
      401:
        description: Could not get choosen preference.
      500:
        description: Internal server error.
    """
    link_mensal = create_payment_monthly()
    link_anual  = create_payment_anual()
    link_eterno = create_payment_eternal()

    if request.method == 'POST':
        try:
            choosen_pref = request.form.get('choosen_preference')
            session['choosen_pref'] = int(choosen_pref)
            return successful_response(
                description="Successfully generated the payment preferences and choosen preference",
                data={"link_anual": link_anual, "link_mensal": link_mensal, "link_eterno": link_eterno})
        
        except Exception as e:
            return error_response(
                description="Could not get choosen preference. Perhaps you forgot to choose the payment type?",
                response=401,
                error_details={"exception": e}
            )
    return render_template("payment_checkout.html")

 
@payment.route('/payment_done')
@login_required
def payment_done():
    """
    Validate signature payment in database.
    ---
    tags:
      - Signature
    parameters:
      - name: choosen_preference
        in: sessionData
        type: int
        required: true
        description: Tag with which signature client is paying for.
    responses:
      200:
        description: Signature successfully added in database.
        schema:
          type: object
          properties:
            link_mensal:
              type: string
              description: URL of the preference created to be paid.
            link_anual:
              type: string
              description: URL of the preference created to be paid.
            link_eterno:
              type: string
              description: URL of the preference created to be paid.
      401:
        description: Couldn't get preference from session.
      500:
        description: Internal server error.
    """
    try:
        choosen_pref = session.get('choosen_pref')
        print(choosen_pref)
        user_id = current_user.get_id()
        signature_gap = get_days_signature(choosen_pref)

        assinatura = Assinaturas(user_id=user_id, 
                                 inicio = datetime.now(), fim = datetime.now()+timedelta(days=signature_gap), 
                                 TipoAssinatura = choosen_pref)
        db.session.add(assinatura)
        db.session.commit()

        return successful_response(description="Signature successfully validated",
                                    response=200)

    except Exception as e:
        return error_response(description="Couldn't get preference from session", response=401, error_details=e)

@payment.route('/payment_denied')
def payment_denied():
    """
    Signature payment denied.
    ---
    tags:
      - Signature
    responses:
      401:
        description: Payment not approved.
      500:
        description: Internal server error.
    """
    return error_response(description="Payment not approved.", response=401)


def get_days_signature(preference: int):
    if preference == 0:
        return 31
    if preference == 1:
        return 365
    if preference == 2:
        return -1