import random
import string
import mailtrap as mt
from .api_key import MAILTRAP_API_KEY
from .json_responses import *

# Utility function to generate a random verification code
def generate_verification_code(length=6):
    """
    Generate a random verification code.

    This function generates a random verification code of a specified length (default is 6).

    ---
    tags:
      - Utility
    parameters:
      - name: length
        in: query
        type: integer
        required: false
        description: The length of the verification code. Default is 6.
    responses:
      200:
        description: A random verification code.
        schema:
          type: string
          example: "123456"
    """
    return ''.join(random.choices(string.digits, k=length))

# Email sending logic
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
            category="Email Verification",
        )
        
        # Send the email
        response = client.send(mail)
        
        if response.status_code == 200:
            return successful_response(description='Email sent successfully.')
        else:
            return error_response(description='Failed to send email via Mailtrap.', error_details=f'Error code: {response.status_code}')
    
    except Exception as e:
        return error_response(description='Error sending email via Mailtrap.', error_details=f'Error: {e}')

# Email verification logic
def send_verification_email(email, verification_code):
    """
    Send a verification email with the code to the user.

    This function sends a verification code to the provided email address.

    ---
    tags:
      - Authentication
    parameters:
      - name: email
        in: query
        type: string
        required: true
        description: The email address to which the verification code will be sent.
      - name: verification_code
        in: query
        type: string
        required: true
        description: The verification code to be sent to the user.
    responses:
      200:
        description: Verification email successfully sent.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Verification email sent."
      500:
        description: Error sending the verification email.
    """
    message = f"Your verification code is: {verification_code}"
    subject = "Email Verification"
    return send_email(email, subject, message)
