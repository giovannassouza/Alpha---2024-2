from flask import Blueprint, session, request, render_template
from flask_login import login_user, login_required, logout_user, current_user
from .models import *
from . import oauth, db, google
from datetime import datetime
from .json_responses import successful_response, error_response
from .utils import send_verification_email, generate_verification_code, validate_cpf, create_user, user_online_check

auth = Blueprint('auth', __name__)

@auth.route('/login/authenticate', methods=['POST', 'GET'])
def login():
    """
    Authenticate user login.
    ---
    tags:
      - Authentication
    parameters:
      - name: csrf_token
        in: formData
        type: string
        required: true
        description: CSRF token for secure requests.
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
      403:
        description: Invalid CSRF token.
      404:
        description: User not found.
      500:
        description: Internal server error.
    """
    if current_user.is_authenticated:
        return error_response(description="Unauthorized access.", response=401)
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')  # Ensure CSRF token exists
        if not csrf_token:
            return error_response(description="Invalid CSRF token.", response=403)
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
        
        if user:
            if user.check_password(user_password):
                login_user(user, remember=keep_logged_in)
                if current_user.is_authenticated:
                    return successful_response(description="Logged in successfully.", data={"user": current_user.email})
                else:
                    return error_response(description="Error logging in.", response=500)
            else:
                return error_response(description="Incorrect password. Check your credentials.", response=401)
        else:
            return error_response(description="User not found. Check your credentials.", response=404)
    
    return render_template('login.html')


@auth.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    """
    Register a new user account.
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
        description: Password confirmation.
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
        description: Invalid input provided (e.g., invalid email, mismatched passwords).
      401:
        description: Unauthorized access.
      403:
        description: Invalid CSRF token.
      409:
        description: Email or CPF already registered.
      500:
        description: Internal server error.
    """
    if current_user.is_authenticated:
        return error_response(description="Unauthorized access.", response=401)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        check_password = request.form.get('password_check')
        full_name = request.form.get('full_name')
        birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d')
        cpf = request.form.get('cpf')
        cliente_tina = request.form.get('cliente_tina')
        keep_logged_in = request.form.get('keep_logged_in')
        
        try:
            if User.query.filter_by(email=email).count() >= 1:
                return error_response(description="Email already registered.", response=409)
        except Exception as e:
            return error_response(description="Database error occurred.", response=500, error_details={"error": str(e)})
        
        if '@' not in email:
            return error_response(description="Invalid email.", response=400)
        
        if password != check_password:
            return error_response(description="Passwords do not match.", response=400)
        
        if birth_date >= datetime.now():
            return error_response(description="Invalid birth date.", response=400)
        
        if not validate_cpf(cpf):
            return error_response(description="Invalid CPF.", response=400)
        
        try:
            if User.query.filter_by(cpf=cpf).count() >= 1:
                return error_response(description="CPF already registered.", response=409)
        except Exception as e:
            return error_response(description="Database error occurred.", response=500, error_details={"error": str(e)})
        
        verification_code = generate_verification_code()
        send_verification_email(email=email, verification_code=verification_code)
        
        # Temporarily store the verification code and user data
        session['verification_code'] = verification_code
        session['pending_user_data'] = {
            'email': email,
            'password': password,
            'full_name': full_name,
            'birth_date': birth_date.strftime('%Y-%m-%d'),
            'cpf': cpf,
            'cliente_tina': cliente_tina,
            'keep_logged_in': keep_logged_in,
        }
        
        return render_template('verify-email.html', email=email)
    
    return render_template('sign-up.html')

@auth.route('/verify-email', methods=['POST'])
def verify_email():
    entered_code = request.form.get('verification_code')
    
    # Retrieve the expected code and user data from the session
    expected_code = session.get('verification_code')
    user_data = session.get('pending_user_data')
    
    if not expected_code or not user_data:
        return error_response(description="Verification process expired. Please try signing up again.", response=400)
    
    if entered_code != expected_code:
        return error_response(description="Invalid verification code.", response=400)
    
    # If the code is valid, create the user account
    user = create_user(
        email=user_data['email'],
        full_name=user_data['full_name'],
        cpf=user_data['cpf'],
        password=user_data['password'],
        data_nasc=datetime.strptime(user_data['birth_date'], '%Y-%m-%d'),
        cliente_tina=user_data['cliente_tina']
    )
    
    # Log the user in
    login_user(user, remember=user_data['keep_logged_in'])
    
    # Clear session data
    session.pop('verification_code', None)
    session.pop('pending_user_data', None)
    
    return successful_response(description="Signed up successfully.", data={"user": current_user.email})

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
    if online_check['response'] != 200:
      return online_check
    logout_user()
    return successful_response(description="Logged out successfully.")


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
