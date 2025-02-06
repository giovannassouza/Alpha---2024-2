from flask import Blueprint, session, request, render_template
from flask_login import login_user, login_required, logout_user, current_user
from .models import *
from . import db
from datetime import datetime
from .json_responses import successful_response, error_response
from .utils import validate_cpf, create_user, user_online_check, send_authentication_email, generate_authentication_code

auth = Blueprint('auth', __name__)


@auth.route('/login/authenticate', methods=['POST', 'GET'])
def login():
    """
    Authenticate user login.
    ---
    tags:
      - Authentication
    parameters:
      - name: id_method
        in: formData
        type: string
        required: true
        description: User email or CPF for identification.
      - name: password
        in: formData
        type: string
        required: true
        description: User password.
      - name: keep_logged_in
        in: formData
        type: boolean
        required: false
        description: Whether to keep the user logged in.
    responses:
      200:
        description: Successfully authenticated user.
        schema:
          type: object
          properties:
            user:
              type: string
              description: Authenticated user email.
      401:
        description: Unauthorized access or incorrect credentials.
      404:
        description: User not found.
      500:
        description: Internal server error.
    """
    if current_user.is_authenticated:
        return error_response(description="Unauthorized access.", response=401)
    if request.method == 'POST':
        id_method = request.form.get('id_method')
        user_password = request.form.get('password')
        keep_logged_in = bool(request.form.get('keep_logged_in'))
        
        try:
            if '@' in id_method:
                user = User.query.filter_by(email=id_method).first()
            else:
                user = User.query.filter_by(cpf=id_method).first()
        except Exception as e:
            return error_response(description="Database error occurred.", response=500, error_details={"error": str(e)})
        
        if (not user) or (not user.is_active):
          return error_response(description="User not found. Check your credentials.", response=404)
        
        if not user.check_password(user_password):
          return error_response(description="Incorrect password. Check your credentials.", response=401)
        
        login_user(user, remember=keep_logged_in)
        
        if not current_user.is_authenticated:
          return error_response(description="Error logging in.", response=500)
        
        return successful_response(description="Logged in successfully.", data={"user": current_user.email})
    
    return render_template('login.html')


@auth.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    """
    Register a new user account.
    
    This endpoint allows users to register for a new account by providing 
    the required details such as email, password, and personal information. 
    It performs input validation and checks for duplicate accounts based on 
    email and CPF. If the registration is successful, the user is logged in 
    automatically.
    
    ---
    tags:
      - Authentication
    parameters:
      - name: email
        in: formData
        type: string
        required: true
        description: User email for registration.
      - name: password
        in: formData
        type: string
        required: true
        description: User password for the account.
      - name: password_check
        in: formData
        type: string
        required: true
        description: Password confirmation (must match the password).
      - name: full_name
        in: formData
        type: string
        required: true
        description: Full name of the user.
      - name: birth_date
        in: formData
        type: string
        required: true
        description: User birth date in YYYY-MM-DD format.
      - name: cpf
        in: formData
        type: string
        required: true
        description: User CPF (Brazilian ID number).
      - name: cliente_tina
        in: formData
        type: boolean
        required: false
        description: Whether the user is a Tina client.
      - name: keep_logged_in
        in: formData
        type: boolean
        required: false
        description: Whether to keep the user logged in after registration.
    responses:
      200:
        description: Successfully registered and logged in.
        schema:
          type: object
          properties:
            user_email:
              type: string
              description: Registered user email.
      400:
        description: Invalid input provided (e.g., invalid email, mismatched passwords, or invalid birth date/CPF).
      401:
        description: Unauthorized access. Occurs if a logged-in user attempts to access the sign-up page.
      409:
        description: Conflict error due to duplicate email or CPF already registered.
      500:
        description: Internal server error. Occurs due to database errors or unexpected server issues.
    """
    def check_credentials(email: str, password: str, check_password: str, birth_date: datetime, cpf: str):
      if '@' not in email:
        return error_response(description="Invalid email.", response=400)
      if password != check_password:
        return error_response(description="Passwords do not match.", response=400)
      if birth_date >= datetime.now():
        return error_response(description="Invalid birth date.", response=400)
      if not validate_cpf(cpf):
        return error_response(description="Invalid CPF.", response=400)
      return successful_response(description="Credentials successfully verified.", response=200)
    
    if current_user.is_authenticated:
      return error_response(description="Unauthorized access.", response=401)
    
    if request.method == 'GET':
      return render_template('sign-up.html')
    
    email = request.form.get('email')
    password = request.form.get('password')
    check_password = request.form.get('password_check')
    full_name = request.form.get('full_name')
    birth_date = datetime.strptime(request.get_json().get('birth_date'), '%Y-%m-%d')
    cpf = request.form.get('cpf')
    cliente_tina = request.form.get('cliente_tina')
    keep_logged_in = request.form.get('keep_logged_in')
    
    try:
      user = User.query.filter_by(email=email).first() # Try finding user with email
    except Exception as e:
      return error_response(description="Database error occurred.", response=500, error_details={"error": str(e)})
    if user: # If there is a user
      if user.is_active: # And if it is active
        return error_response(description="Email already registered.", response=409) # Then, don't allow signup
      # If there is a user but they aren't active
      check_credentials = check_credentials(email, password, check_password, birth_date, cpf) # Check credentials
      if check_credentials.status_code != 200:
        return check_credentials
      # Proceed with the signup
      user.full_name = full_name
      user.email = email
      user.cpf = cpf
      user.data_nasc = birth_date
      user.cliente_tina = cliente_tina
      user.set_password(password)
      if user.email == 'es.grupoalpha2024@gmail.com':
        user.is_adm = True
      db.session.commit()
      login_user(user, remember=keep_logged_in)
      if current_user.is_authenticated:
        return successful_response(description="Signed up successfully.", data={"user_email": current_user.email})
      return error_response(description="Signed up but error logging in.", response=500)
    
    # Repeat the same process with cpf
    try:
      user = User.query.filter_by(cpf=cpf).first() # Try finding user with cpf
    except Exception as e:
      return error_response(description="Database error occurred.", response=500, error_details={"error": str(e)})
    if user: # If there is a user
      if user.is_active: # And if it is active
        return error_response(description="CPF already registered.", response=409) # Then, don't allow signup
      # If there is a user but they aren't active
      check_credentials = check_credentials(email, password, check_password, birth_date, cpf) # Check credentials
      if check_credentials.status_code != 200:
        return check_credentials
      # Proceed with the signup
      user.full_name = full_name
      user.email = email
      user.cpf = cpf
      user.data_nasc = birth_date
      user.cliente_tina = cliente_tina
      user.set_password(password)
      if user.email == 'es.grupoalpha2024@gmail.com':
        user.is_adm = True
      db.session.commit()
      login_user(user, remember=keep_logged_in)
      if current_user.is_authenticated:
        return successful_response(description="Signed up successfully.", data={"user_email": current_user.email})
      return error_response(description="Signed up but error logging in.", response=500)
    
    # If there isn't a user
    user = create_user( # Create one
        email=email,
        full_name=full_name,
        cpf=cpf,
        password=password,
        data_nasc=birth_date,
        is_adm=True if email == 'es.grupoalpha2024@gmail.com' else False,
        cliente_tina=cliente_tina
    )
    
    login_user(user, remember=keep_logged_in)
    if current_user.is_authenticated:
      return successful_response(description="Signed up successfully.", data={"user_email": current_user.email})
    return error_response(description="Signed up but error logging in.", response=500)

@auth.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    """
    Log out the current user.
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Successfully logged out.
      401:
        description: Unauthorized access (user not logged in).
    """
    online_check = user_online_check()
    if online_check.status_code != 200:
      return online_check
    logout_user()
    return successful_response(description="Logged out successfully.")


@auth.route('/authenticate/send-email', methods=['POST'])
@login_required
def send_authentication_code_email():
  """
  Sends an authentication code to the user's registered email.
  
  ---
  tags:
    - Authentication
  summary: Send email authentication code
  description: This endpoint sends a unique email authentication code to the provided email address. A user with the email must exist, and their email must not already be authenticated.
  responses:
    200:
      description: Authentication code sent successfully.
      schema:
        type: object
        properties:
          description:
            type: string
            example: "Authentication code sent to your email ****@domain.com. Check SPAM."
          response:
            type: integer
            example: 200
    401:
      description: Email already authenticated or unauthorized access.
      schema:
        type: object
        properties:
          description:
            type: string
            example: "Email already authenticated."
          response:
            type: integer
            example: 401
    403:
      description: Unauthorized access. User is not authenticated.
      schema:
        type: object
        properties:
          description:
            type: string
            example: "Unauthorized access."
          response:
            type: integer
            example: 403
    500:
      description: Error sending the email.
      schema:
        type: object
        properties:
          description:
            type: string
            example: "Failed to send the authentication code email."
          response:
            type: integer
            example: 500
  """
  email = request.form.get("email")
  if not email:
    return error_response(description='Email not provided.', response=400)
  
  try:
    user = User.query.filter_by(email=email).first()
  except Exception as e:
    return error_response(description="Database error occurred.", response=500, error_details={"error": str(e)})
  if not user:
    return error_response(description="There isn't a user with this email.", response=400)
  
  if user.email_authenticated:
    return error_response(description='Email already authenticated.', response=401)
  
  authentication_code = generate_authentication_code()
  response = send_authentication_email(user.email, authentication_code)
  if response.status_code != 200:
    return response
  
  user.email_authentication_code = authentication_code
  db.session.commit()
  session['authentication_email'] = email
  return successful_response(description=f'Authentication code sent to your email {current_user.email[:4]+"***"+current_user.email[-9:]}. Check SPAM.', response=200)

@auth.route('/authenticate/email-auth-code', methods=['POST'])
@login_required
def authenticate_email_code():
  """
  Verifies the provided email authentication code.
  
  ---
  tags:
    - Authentication
  summary: Authenticate email using a authentication code
  description: This endpoint verifies the email authentication code provided by the user. The user must have requested the authentication code in the same session and their email must not already be authenticated. If the code matches, the user's email will be authenticated.
  consumes:
    - application/x-www-form-urlencoded
  parameters:
    - name: auth-code
      in: formData
      type: string
      required: true
      description: The email authentication code sent to the user's registered email.
  responses:
    200:
      description: Email authenticated successfully.
      schema:
        type: object
        properties:
          description:
            type: string
            example: "Email authenticated successfully."
          response:
            type: integer
            example: 200
    400:
      description: Invalid or missing authentication code.
      schema:
        type: object
        properties:
          description:
            type: string
            example: "Authentication code not provided."
          response:
            type: integer
            example: 400
    401:
      description: Email already authenticated or unauthorized access.
      schema:
        type: object
        properties:
          description:
            type: string
            example: "Email already authenticated."
          response:
            type: integer
            example: 401
    403:
      description: Unauthorized access. User is not authenticated.
      schema:
        type: object
        properties:
          description:
            type: string
            example: "Unauthorized access."
          response:
            type: integer
            example: 403
  """
  email = session['authentication_email']
  session.pop('authentication_email', None)
  try:
    user = User.query.filter_by(email=email).first()
  except Exception as e:
    return error_response(description="Database error occurred.", response=500, error_details={"error": str(e)})
  if not user:
    return error_response(description="There isn't a user with this email.", response=400)
  
  if user.email_authenticated:
    return error_response(description='Email already authenticated.', response=401)
  
  provided_auth_code = request.form.get('auth-code')
  if not provided_auth_code:
    return error_response(description='Authentication code not provided.', response=400)
  
  if provided_auth_code != user.email_authentication_code:
    return error_response('Invalid authentication code. Try again. Check you email (and SPAM).', response=400)
  user.email_authenticated = True
  user.email_authentication_code = None
  db.session.commit()
  return successful_response('Email authenticated successfully.', response=200)

def validate_signature(user: User):
    """
    Validate user subscription.
    ---
    tags:
      - Signature
    parameters:
      - name: user
        in: body
        type: User
        required: true
        description: Logged in user.
    responses:
      200:
        description: subscription succesfully validated.
      400:
        description: Expired subscription.
      401:
        description: Couldn't find subscription in database.
    """

    try:
        signature = Assinaturas.query.filter_by(user_id= user.id).first()
        if not signature:
          return ValueError("No subscription found in database.")
        if signature.fim < datetime.date.now():
          user.assinante = 0
          db.session.commit()
          return ValueError("Expired subscription.")
        else:
          user.assinante = 1
          db.session.commit()
          return successful_response(description="Subscription successfully validated.", data={"fim_assinatura": signature.fim})
    except Exception as e:
        return error_response(description="Couldn't find subscription in database.", response=401, error_details={"Exception": str(e)})


'''
@auth.route('/login/google') # Login for google
def login_google():
    try:
        redirect_uri = url_for('authorize_google', _external=True)
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        #app.logger.error()
        return 'An error occured while logging in.', 500

@auth.route('/authorize/google')
def authorize_google():
    token = google.authorize_access_token()
    userinfo_endpoint = google.server_metadata['userinfo_endpoint']
    resp = google.get(userinfo_endpoint)
    user_info = resp.json()
    email = user_info.get('email')
    
    try:
        user = User.query.filter_by(email=email)
    except Exception as e:
        return error_response(description="Database error occurred.", response=500, error_details={"error": str(e)})
    
    if not user:
        response = create_user(
            email = email,
            full_name = user_info.get('name'),
            google_linked = True
            )
    
    if 'Error' not in response:
        session['user_email'] = email
        session['oauth_token'] = token.get('access_token')
        session['user_is_logged_in'] = True
    
    return redirect('/')
'''
