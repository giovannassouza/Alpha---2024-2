from datetime import datetime, timedelta
from flask import Blueprint, Flask, jsonify, render_template, request, session, redirect, url_for
from flask_login import login_required, current_user
from website.auth import validate_signature
from website.models import *
from .json_responses import successful_response, error_response
from .payment_api import create_payment_eternal, create_payment_anual, create_payment_monthly

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
            choosen_pref = request.form.get('choosen_preference')
            if not choosen_pref:
                raise ValueError("Preference not selected.")

            # Armazena a preferência na sessão
            session['choosen_pref'] = int(choosen_pref)
            print(f"Preference stored in session: {session['choosen_pref']}")

            # Redireciona para a página de pagamento concluído
            return successful_response(
                description="Successfully generated the payment preferences and choosen preference",
                data={"link_anual": link_anual, "link_mensal": link_mensal, "link_eterno": link_eterno}
            )


        except Exception as e:
            return error_response(
                description="Could not get choosen preference. Perhaps you forgot to choose the payment type?",
                response=401,
                error_details={"exception": str(e)}
            )

    return render_template("payment.html", link_eterno=link_eterno, link_mensal=link_mensal, link_anual=link_anual)


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
      401:
        description: Couldn't get preference from session.
      500:
        description: Internal server error.
    """
    try:
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
        db.session.commit()

        return successful_response(description="Signature successfully created", response=200)

    except Exception as e:
        return error_response(description="Couldn't get preference from session", response=401, error_details={"exception": str(e)})


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

@payment.route('/signature_manager')
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
    if request.method == 'GET':
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
    if preference == 0:  # Mensal
        return 31
    elif preference == 1:  # Anual
        return 365
    elif preference == 2:  # Vitalício
        return -1  # -1 indica assinatura vitalícia
    else:
        raise ValueError(f"Invalid preference value: {preference}")