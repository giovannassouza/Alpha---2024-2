from flask import Blueprint, url_for, redirect, session, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from models import User
from . import oauth, db, google
from website.models import *
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login/authenticate', methods=['POST'])
def login():
    if request.method == 'POST':
        user_email = request.form.get('email')
        user_password = request.form.get('password')
        keep_logged_in = request.form.get('keep_logged_in')
        
        user = User.query.filter_by(email=user_email).first()
        
        if user.check_password(user_password):
            login_user(user, remember=keep_logged_in)
            if current_user.is_authenticated:
                flash('Logged in successfully.', category='success')
            else:
                flash('Error logging in.', category='error')
        else:
            flash('Incorrect information. Verify your credentials and try again.', category='error')

@auth.route('/sign-up', methods=['POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        check_password = request.form.get('password_check')
        full_name = request.form.get('full_name')
        birth_date = request.form.get('birth_date')
        cpf = request.form.get('cpf')
        keep_logged_in = request.form.get('keep_logged_in')
        
        if User.query.filter_by(email=email).count() >= 1:
            flash('Email already registered in our database.', category='error')
            return redirect(url_for('views.login'))
        if '@' not in email:
            flash('Invalid email. Check your credentials.', category='error')
            return redirect(url_for('views.sign_up'))
        if password != check_password:
            flash('Passwords do not match.', category='error')
            return redirect(url_for('views.sign_up'))
        if birth_date > datetime.now():
            flash('Invalid birth date. Check your credentials.', category='error')
            return redirect(url_for('views.sign_up'))
        
        response = create_user(
            email = email,
            full_name = full_name,
            cpf = cpf,
            password = password,
            data_nasc = datetime.strptime(birth_date, '%Y-%m-%d')
        )
        
        if 'Error' in response:
            flash('Error signing up.', category='error')
            return redirect(url_for('views.sign_up'))
        else:        
            login_user(User.query.filter_by('email').first(), remember=keep_logged_in)
            if current_user.is_authenticated:
                flash('Signed up successfully.', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Error logging in. Try again.', category='error')
                return redirect(url_for('views.login'))

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
    
    user = User.query.filter_by(email=email)
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

def create_user(email: str, full_name: str, cpf: str = None, password: str = None, data_nasc: datetime = None, data_criacao: datetime = datetime.now(), google_linked: bool = False):
    if cpf != None:
        if not validate_cpf(cpf):
            flash('Invalid CPF. Try again.', category= 'error')
            return 'Error. Invalid CPF'
    
    new_user = User(
        email = email,
        cpf = cpf,
        password = password if password == None else User.set_password(password),
        full_name = full_name,
        data_nasc = data_nasc,
        data_criacao = data_criacao,
        google_linked = google_linked
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return 'Success. User created.'

def user_is_logged():
    return True if type(session['user_email']) == str else False

@auth.route('/update-info', methods=['POST'])
def update_info():
    if request.method == 'POST':
        user_email = session['user_email']
        if user_is_logged():
            cpf = request.form.get('cpf')
            birth_date = request.form.get('birth_date')
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
            if birth_date > datetime.now():
                flash('Invalid date. Review your information.', category='error')
            else:
                user = User.query.filter_by(email=user_email)
                user.data_nasc = birth_date
            if validate_cpf(cpf):
                user.cpf = cpf
            else:
                flash('Invalid CPF. Check your credentials.', category='error')
            db.session.commit()
    return 'Updated successfully.'

def validate_cpf(cpf: str) -> bool:
    # Step 1: Clean the CPF (remove non-numeric characters)
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Step 2: Check length and invalid patterns
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Step 3: Calculate the first check digit
    def calculate_digit(cpf_part):
        weight = len(cpf_part) + 1
        total = sum(int(digit) * (weight - idx) for idx, digit in enumerate(cpf_part))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    first_digit = calculate_digit(cpf[:9])
    second_digit = calculate_digit(cpf[:9] + str(first_digit))

    # Step 4: Validate against provided check digits
    return cpf == cpf[:9] + str(first_digit) + str(second_digit)