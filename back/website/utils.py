import random
import string
import mailtrap as mt
from .api_key import MAILTRAP_API_KEY
from .json_responses import *
from flask import Blueprint, Response
from flask_login import current_user
from .models import *
from . import db
from datetime import datetime
from .json_responses import successful_response, error_response
import json

utils = Blueprint('utils', __name__)

def response_to_dict(response: Response) -> dict:
    """
    Convert a Flask Response object containing JSON data to a Python dictionary.
    
    :param response: Flask Response object
    :return: Python dictionary
    """
    return json.loads(response.get_data(as_text=True))

# Utility function to generate a random authentication code
def generate_authentication_code(length=6):
    """
    Generate a random authentication code.

    This function generates a random authentication code of a specified length (default is 6).

    ---
    tags:
      - Utility
    parameters:
      - name: length
        in: query
        type: integer
        required: false
        description: The length of the authentication code. Default is 6.
    responses:
      200:
        description: A random authentication code.
        schema:
          type: string
          example: "123456"
    """
    return ''.join(random.choices(string.digits, k=length))

# Email sending logic
@utils.route("/send-email")
def send_email(recipient: str, subject: str, message: str):
    """
    Send an email via Mailtrap.

    This function sends an email using the Mailtrap service. The email is sent with the specified
    recipient, subject, and message body.

    ---
    tags:
      - Email
    parameters:
      - name: recipient
        in: query
        type: string
        required: true
        description: The email address of the recipient.
      - name: subject
        in: query
        type: string
        required: true
        description: The subject of the email.
      - name: message
        in: query
        type: string
        required: true
        description: The body message of the email.
    responses:
      200:
        description: Email successfully sent.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Email sent successfully."
      400:
        description: Invalid request data.
      500:
        description: Error sending email via Mailtrap.
    """
    try:
        # Set up the Mailtrap client
        client = mt.MailtrapClient(token=MAILTRAP_API_KEY)
        
        # Set up the email components
        mail = mt.Mail(
            sender=mt.Address(email="hello@demomailtrap.com", name="Mailtrap Test"),
            to=[mt.Address(email=recipient)],
            subject=subject,
            text=message,
            category="Email authentication",
        )
        
        # Send the email
        response = client.send(mail)
        
        if response.status_code == 200:
            return successful_response(description='Email sent successfully.')
        else:
            return error_response(description='Failed to send email via Mailtrap.', error_details=f'Error code: {response.status_code}')
    
    except Exception as e:
        return error_response(description='Error sending email via Mailtrap.', error_details=f'Error: {e}')

# Email authentication logic
@utils.route("/send-authentication-email")
def send_authentication_email(email, authentication_code):
    """
    Send a authentication email with the code to the user.

    This function sends a authentication code to the provided email address.

    ---
    tags:
      - Authentication
    parameters:
      - name: email
        in: query
        type: string
        required: true
        description: The email address to which the authentication code will be sent.
      - name: authentication_code
        in: query
        type: string
        required: true
        description: The authentication code to be sent to the user.
    responses:
      200:
        description: authentication email successfully sent.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "authentication email sent."
      500:
        description: Error sending the authentication email.
    """
    message = f"Your authentication code is: {authentication_code}"
    subject = "Email authentication"
    return send_email(email, subject, message)

@utils.route("/create-user")
def create_user(
    email: str,
    full_name: str,
    cpf: str = None,
    password: str = None,
    data_nasc: datetime = None,
    data_criacao: datetime = datetime.now(),
    is_adm: bool = False,
    cliente_tina: bool = False
    ):
    """
    Create a new user in the database.
    ---
    tags:
      - User Management
    parameters:
      - name: email
        in: body
        type: string
        required: true
        description: User email.
      - name: full_name
        in: body
        type: string
        required: true
        description: Full name of the user.
      - name: cpf
        in: body
        type: string
        required: false
        description: CPF of the user.
      - name: password
        in: body
        type: string
        required: false
        description: Password of the user.
      - name: data_nasc
        in: body
        type: string
        required: false
        description: Birth date of the user in YYYY-MM-DD format.
      - name: cliente_tina
        in: body
        type: boolean
        required: false
        description: Whether the user is a Tina client.
    responses:
      201:
        description: User successfully created.
      400:
        description: Invalid input.
      500:
        description: Database error occurred.
    """
    if cpf != None:
        if not validate_cpf(cpf):
            return 'Error. Invalid CPF.'
    
    new_user = User(
        email = email,
        cpf = cpf,
        password = None,
        full_name = full_name,
        data_nasc = data_nasc,
        data_criacao = data_criacao,
        is_adm = 1 if is_adm else 0,
        cliente_tina = 1 if cliente_tina else 0
    )
    
    if password:
        new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return new_user

def validate_cpf(cpf: str) -> bool:
    """
    Validate a CPF number.
    ---
    tags:
      - Validation
    parameters:
      - name: cpf
        in: body
        type: string
        required: true
        description: CPF number to validate.
    responses:
      200:
        description: CPF is valid.
      400:
        description: CPF is invalid.
    """
    cpf = ''.join(filter(str.isdigit, cpf))
    
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    def calculate_digit(cpf_part):
        weight = len(cpf_part) + 1
        total = sum(int(digit) * (weight - idx) for idx, digit in enumerate(cpf_part))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
    first_digit = calculate_digit(cpf[:9])
    second_digit = calculate_digit(cpf[:9] + str(first_digit))

    return cpf == cpf[:9] + str(first_digit) + str(second_digit)


@utils.route("/utils/user_online_check")
def user_online_check():
    """
    Verifies if the user is authenticated.

    ---
    tags:
      - User Authentication
    summary: Check user authentication status
    description: This endpoint checks if the current user is authenticated. Returns appropriate error responses if the user is not authenticated.
    responses:
      200:
        description: User is authenticated.
        schema:
          type: object
          properties:
            description:
              type: string
              example: User is authenticated
            response:
              type: integer
              example: 200
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
    if not current_user.is_authenticated:
        return error_response(description="Unauthorized access.", response=401)
    return successful_response(description="User is authenticated", response=200)