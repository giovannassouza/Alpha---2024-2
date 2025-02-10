from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, session
from flask_login import login_required, current_user
from website.auth import validate_signature
from website.models import *
from .json_responses import successful_response, error_response
from .payment_api import create_payment_eternal, create_payment_anual, create_payment_monthly
import secrets

payment = Blueprint('payment', __name__)

@payment.route('/payment_checkout', methods=["GET", "POST"])
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
            payment_url:
              type: string
              description: URL of the preference created to be paid.
      401:
        description: Could not get choosen preference.
      500:
        description: Internal server error.
    """
    # Código para saber se o user ja tem assinatura vigente
    user_id = current_user.get_id()
    try:
      user = User.query.filter_by(id=user_id).first()
      validate_signature(user=user)
      if user.assinante:
          return error_response(description="Unauthorized access.", response=401, error_details={"exception": "User already has a current subscription."})
    except Exception as e:
        return error_response(description="Couldn't access database", response=500)
    
    link_mensal = create_payment_monthly()
    link_anual = create_payment_anual()
    link_eterno = create_payment_eternal()

    if request.method == 'POST':
      try:
        data = request.get_json()
        choosen_pref = data.get('choosen_pref')
        if not choosen_pref:
          raise ValueError("Preference not selected.")
        if choosen_pref>3 or choosen_pref<1:
          raise ValueError("Preference not acceptable")
        
        # Armazena a preferência na sessão
        session['choosen_pref'] = int(choosen_pref)
        payment_token = secrets.token_urlsafe(16)
        session['payment_token'] = payment_token

        if(choosen_pref==1):
          payment_url = f"{link_mensal}?token={payment_token}"
        if(choosen_pref==2):
          payment_url = f"{link_anual}?token={payment_token}"
        if(choosen_pref==3):
          payment_url = f"{link_eterno}?token={payment_token}"

        return successful_response(description="Succesfully generated selected payment preference.",
                                data= {"payment_url": payment_url})

      except Exception as e:
          return error_response(
              description="Could not get choosen preference.",
              response=401,
              error_details={"exception": str(e)}
          )

    return render_template("payment.html", link_eterno=link_eterno, link_mensal=link_mensal, link_anual=link_anual)


@payment.route('/payment_done', methods=["GET", "POST"])
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
      - name: token
        in: formData
        type: string
        required: true
        description: Token sent when redirected to payment (checks if client came from payment api's link)
    responses:
      200:
        description: Signature successfully added in database.
      401:
        description: Couldn't get preference from session.
      500:
        description: Internal server error.
    """
    if request.method == "POST":
      try:
          token = request.get_json().get('token')
          if not token or token != session.get('payment_token'):
            raise ValueError("Invalid or missing payment token.")
          
          session.pop('payment_token', None)

          choosen_pref = session.get('choosen_pref')
          if choosen_pref is None:
              raise ValueError("Preference not found in session.")

          print(f"Preference retrieved from session: {choosen_pref}")
          user_id = current_user.get_id()
          signature_gap = get_days_signature(choosen_pref)

          if signature_gap == -1:
              # Assinatura vitalícia (sem data de término)
              assinatura = Assinaturas(
                  user_id=user_id,
                  inicio=datetime.now(),
                  fim=None, 
                  TipoAssinatura=choosen_pref
              )
          else:
              # Assinatura com data de término
              assinatura = Assinaturas(
                  user_id=user_id,
                  inicio=datetime.now(),
                  fim=datetime.now() + timedelta(days=signature_gap),
                  TipoAssinatura=choosen_pref
              )

          db.session.add(assinatura)
          user = User.query.filter_by(id = current_user.get_id()).first()
          user.assinante = True
          db.session.commit()

          return successful_response(description="Signature successfully created", response=200)

      except Exception as e:
          return error_response(description="Couldn't validate signature", response=401, error_details={"exception": str(e)})


@payment.route('/payment_denied')
@login_required
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

@payment.route('/signature_manager', methods=["POST"])
@login_required
def signature_manager():
    """
    Manage user signature.
    ---
    tags:
      - Signature
    responses:
      200:
        description: Successfully accessed active subscription.
        schema:
          type: object
          properties:
            data_inicio:
              type: string
              description: Start date of the subscription.
            data_fim:
              type: string
              description: End date of the subscription.
            tipo_assinatura:
              type: int
              description: Type of subscription.
      404:
        description: Could not find active subscription.
      500:
        description: Internal server error.
    """
    if request.method == 'POST':
      user_id = current_user.get_id()
      try:
          user = User.query.filter_by(id=user_id).first()
          validate_signature(user=user)

          subscription = Assinaturas.query.filter_by(user_id=user_id).first()
          return successful_response(description="Succesfully accessed active subscription.", 
                                    data={"data_inicio": subscription.inicio, "data_fim": subscription.fim, "tipo_assinatura": subscription.TipoAssinatura})
      except Exception as e:
          return error_response(description="Could not find active subscription", error_details={"exception": str(e)})


def get_days_signature(preference: int):
    """
    Retorna o número de dias com base no tipo de assinatura escolhida.
    """
    if preference == 1:  # Mensal
        return 31
    elif preference == 2:  # Anual
        return 365
    elif preference == 3:  # Vitalício
        return -1  # -1 indica assinatura vitalícia
    else:
        raise ValueError(f"Invalid preference value: {preference}")