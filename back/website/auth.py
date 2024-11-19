from flask import Blueprint, url_for, redirect, session, request, flash
from . import oauth, db, google
from website.models import *
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login/google') # Login for google
def login_google():
    try:
        redirect_uri = url_for('authorize_google', _external=True)
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        #app.logger.error()
        return 'An error occured during login', 500

@auth.route('/authorize/google')
def authorize_google():
    token = google.authorize_access_token()
    userinfo_endpoint = google.server_metadata['userinfo_endpoint']
    resp = google.get(userinfo_endpoint)
    user_info = resp.json()
    email = user_info.get('email')
    
    user = User.query.filter_by(email=email)
    if not user:
        user = create_user(
            email = email,
            full_name = user_info.get('name'),
            google_linked = True
            )
    
    session['user_email'] = email
    session['oauth_token'] = token.get('access_token')
    session['user_is_logged_in'] = True
    
    return redirect('/')

def create_user(email: str, full_name: str, cpf: str = None, password: str = None, data_nasc: datetime = None, data_criacao: datetime = datetime.now(), google_linked: bool = False):
    new_user = User(
        email = email,
        cpf = cpf,
        password = password,
        full_name = full_name,
        data_nasc = data_nasc,
        data_criacao = data_criacao,
        google_linked = 1 if google_linked else 0
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user

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