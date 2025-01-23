from flask import Blueprint, url_for, redirect, session, request, render_template
from flask_login import login_user, login_required, logout_user, current_user
from .models import *
from . import oauth, db, google
from datetime import datetime
from .json_responses import successful_response, error_response  # Import your standardized response functions

auth = Blueprint('auth', __name__)

@auth.route('/login/authenticate', methods=['POST', 'GET'])
def login():
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
        
        user = create_user(
            email=email,
            full_name=full_name,
            cpf=cpf,
            password=password,
            data_nasc=birth_date,
            cliente_tina=cliente_tina
        )
        
        login_user(user, remember=keep_logged_in)
        if current_user.is_authenticated:
            return successful_response(description="Signed up successfully.", data={"user": current_user.email})
        else:
            return error_response(description="Signed up but error logging in.", response=500)
    
    return render_template('sign-up.html')


@auth.route('/logout')
@login_required
def logout():
    if not current_user.is_authenticated:
        return error_response(description="Unauthorized access.", response=401)
    logout_user()
    return successful_response(description="Logged out successfully.")


@auth.route('/account-info', methods=['POST', 'GET'])
@login_required
def update_account():
    if request.method == 'POST':
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

def create_user(
    email: str,
    full_name: str,
    cpf: str = None,
    password: str = None,
    data_nasc: datetime = None,
    data_criacao: datetime = datetime.now(),
    google_linked: bool = False,
    cliente_tina: bool = False
    ):
    
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
        cliente_tina = 1 if cliente_tina else 0,
        google_linked = google_linked
    )
    
    if password:
        new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return new_user

def validate_cpf(cpf: str) -> bool:
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
