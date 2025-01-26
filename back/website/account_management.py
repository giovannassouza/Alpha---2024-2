from flask import Blueprint, url_for, redirect, session, request, render_template
from flask_login import login_user, login_required, logout_user, current_user
from .models import *
from . import db
from datetime import datetime
from .json_responses import successful_response, error_response  # Import your standardized response functions
from .utils import validate_cpf, user_online_check

account_management = Blueprint('account_management', __name__)

@account_management.route("/account/deactivate", methods=['POST'])
def deactivate_account():
    """
    Deactivates the account of the currently authenticated user.

    ---
    tags:
      - Account Management
    summary: Deactivate user account
    description: This endpoint deactivates the account of the currently authenticated user after verifying their authentication and confirming the deactivation with a specific confirmation word ("DELETE").
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - name: csrf_token
        in: formData
        type: string
        required: true
        description: CSRF token for the current session.
      - name: confirm
        in: formData
        type: string
        required: true
        description: Confirmation word ("DELETE") required for deactivation.
    responses:
      200:
        description: Account deactivated successfully.
        schema:
          type: object
          properties:
            description:
              type: string
              example: Account deactivated successfully.
            response:
              type: integer
              example: 200
      400:
        description: Invalid confirmation word or bad request.
        schema:
          type: object
          properties:
            description:
              type: string
              example: Invalid confirmation word check.
            response:
              type: integer
              example: 400
      401:
        description: Unauthorized access. User is not authenticated.
        schema:
          type: object
          properties:
            description:
              type: string
              example: Unauthorized access.
            response:
              type: integer
              example: 401
    """
    online_check = user_online_check()
    if online_check['response'] != 200:
        return online_check
    confirm = request.form.get('confirm')
    if confirm != "DELETE":
        return error_response(description="Invalid confirmation word check.", response=400)
    current_user.is_active = False
    logout_user()
    return successful_response(description="Account deactivated successfully.")


@account_management.route('/account/info', methods=['POST', 'GET'])
@login_required
def update_account():
    """
    Update user account information.
    ---
    tags:
      - Account Management
    parameters:
      - name: csrf_token
        in: header
        type: string
        required: true
        description: CSRF token for secure requests.
      - name: full_name
        in: formData
        type: string
        required: false
        description: New full name for the account.
      - name: email
        in: formData
        type: string
        required: false
        description: New email for the account.
      - name: cpf
        in: formData
        type: string
        required: false
        description: New CPF (Brazilian ID number).
      - name: data_nasc
        in: formData
        type: string
        required: false
        description: New birth date in YYYY-MM-DD format.
      - name: cliente_tina
        in: formData
        type: boolean
        required: false
        description: Whether the user is a Tina client.
      - name: old_password
        in: formData
        type: string
        required: true
        description: Current password for verification.
      - name: new_password
        in: formData
        type: string
        required: false
        description: New password for the account.
      - name: check_new_password
        in: formData
        type: string
        required: false
        description: Confirmation of the new password.
    responses:
      200:
        description: Account successfully updated.
        schema:
          type: object
          properties:
            user:
              type: string
              description: Updated user email.
      400:
        description: Invalid input provided.
      401:
        description: Unauthorized access (user not logged in).
      403:
        description: Invalid CSRF token.
      500:
        description: Internal server error.
    """
    if request.method == 'POST':
        online_check = user_online_check()
        if online_check['response'] != 200:
            return online_check
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        cpf = request.form.get('cpf')
        data_nasc = request.form.get('data_nasc')
        cliente_tina = request.form.get('cliente_tina')
        keep_logged_in = request.form.get('keep_logged_in')
        
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        new_password_check = request.form.get('check_new_password')
        
        if current_user:
            if full_name:
                current_user.full_name = full_name
            
            if email:
                current_user.email = email
            
            if cpf and validate_cpf(cpf):
                current_user.cpf = cpf
            
            if data_nasc:
                try:
                    data_nasc = datetime.strptime(data_nasc, '%Y-%m-%d').date()
                    if data_nasc < datetime.now().date():
                        current_user.data_nasc = data_nasc
                except ValueError:
                    return error_response(description="Invalid date format. Use YYYY-MM-DD.", response=400)
            
            
            if cliente_tina:
                current_user.cliente_tina = cliente_tina
            
            if new_password:
                if current_user.check_password(old_password):
                    if new_password == new_password_check:
                        current_user.set_password(new_password)
            
            db.session.commit()
            login_user(current_user, remember=keep_logged_in)
            return successful_response(description="Account updated successfully.", data={"user": current_user.email})
        else:
            return error_response(description="You are not logged in.", response=401)
    
    return render_template('account-info.html')


@account_management.route('/account/lost', methods=['GET'])
@login_required
def lost_account():
  online_check = user_online_check()
  if online_check['response'] != 200:
    return online_check
  if not current_user.email_authenticated:
    return error_response(description='Email must be authenticated first.', response=401)