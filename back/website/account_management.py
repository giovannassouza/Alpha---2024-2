from flask import Blueprint, url_for, redirect, session, request, render_template
from flask_login import login_user, login_required, logout_user, current_user
from .models import *
from . import db
from datetime import datetime
from .json_responses import successful_response, error_response  # Import your standardized response functions
from .utils import validate_cpf, user_online_check, send_email
import random

account_management = Blueprint('account_management', __name__)


@account_management.route('/account/call', methods=["GET"])
@login_required
def call_user():
    """
    Retrieve the current user's account information.

    This endpoint returns the logged-in user's details, including their full name, 
    email, and CPF. It ensures the user is online before retrieving the data.

    ---
    tags:
      - Account Management
    responses:
      200:
        description: Successfully retrieved user information.
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  description: Full name of the user.
                email:
                  type: string
                  description: Email address of the user.
                cpf:
                  type: string
                  description: CPF (Brazilian ID number) of the user.
      401:
        description: User is not logged in.
      500:
        description: Internal server error due to an issue with the online check.
    """
    online_check = user_online_check()
    if online_check.status_code != 200:
        return online_check
    return successful_response(
        description='User data collected successfully.',
        response=200,
        data={
            'name': current_user.full_name,
            'email': current_user.email,
            'cpf': current_user.cpf,
            'is_adm': current_user.is_adm,
            'birth_date': current_user.data_nasc
        }
    )



@account_management.route('/account/lost', methods=['POST'])
@login_required
def lost_account():
    """
    Handle account recovery by generating and sending a new password.

    This endpoint allows users to recover their account by generating a 
    new temporary password and sending it to their registered email address. 
    Only authenticated users with a verified email can use this functionality.

    ---
    tags:
      - Account Management
    requestBody:
      required: true
      content:
        application/x-www-form-urlencoded:
          schema:
            type: object
            properties:
              email:
                type: string
                description: Email address of the user requesting password recovery.
                example: "user@example.com"
    responses:
      200:
        description: New password sent to the user's email inbox.
      401:
        description: Email must be authenticated before password recovery.
      404:
        description: User with the provided email not found.
      500:
        description: Internal server error, such as database issues or email-sending failure.
    """
    email = request.form.get("email")
    try:
        user = User.query.filter_by(email=email)
    except Exception as e:
        return error_response(description="Database error occurred.", response=500, error_details={"error": str(e)})
    
    if not current_user.email_authenticated:
        return error_response(description='Email must be authenticated first.', response=401)
    
    # Generate a new temporary password
    new_password = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    user.set_password(password=new_password)
    
    # Send email with the new password
    response = send_email(
        recipient=email,
        subject="New password for Tina: Gestão de Cantinas",
        message=f"Use this password to access your account.\n"
                f"Remember to change it as soon as possible.\n\nYour password is '{new_password}'"
    )
    if response.status_code != 200:
        return response
    return successful_response(description="New password sent to user's email inbox.", response=200)



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
    if online_check.status_code != 200:
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
      500:
        description: Internal server error.
    """
    if request.method == 'POST':
        online_check = user_online_check()
        if online_check.status_code != 200:
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
