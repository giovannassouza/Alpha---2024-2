from website.models import User
from website.auth import validate_cpf, checked_in
from datetime import datetime

def test_signup(client, app):
    response = client.post(
        '/sign-up',
        data={
            'email': 'test@test.com',
            'password': 'test1234',
            'password_check': 'test1234',
            'full_name': 'Tester',
            'birth_date': datetime.strptime('01/01/2000', '%d/%m/%Y'),
            'cpf': '539.529.150-41', # Aleatório
            'keep_logged_in': True
        }
    )
    
    with app.app_context():
        assert User.query.count() == 1
        assert User.query.first().email == 'test@test.com'
        assert User.query.first().full_name == 'Tester'
        assert User.query.first().check_password('test1234')
        assert User.query.first().data_nasc == datetime.strptime('01/01/2000', '%d/%m/%Y')
        assert User.query.first().cpf == '539.529.150-41'

def test_signup_email_exists(client, app):
    response = client.post(
        '/sign-up',
        data={
            'email': 'test@test.com',
            'password': 'test1234',
            'password_check': 'test1234',
            'full_name': 'Tester',
            'birth_date': datetime.strptime('01/01/2000', '%d/%m/%Y'),
            'cpf': '539.529.150-41', # Aleatório
            'keep_logged_in': True
        }
    )      
    response = client.post(
        '/sign-up',
        data={
            'email': 'test@test.com',
            'password': 'test1234',
            'password_check': 'test1234',
            'full_name': 'Tester2',
            'birth_date': datetime.strptime('01/01/2000', '%d/%m/%Y'),
            'cpf': '199.743.100-91', # Aleatório
            'keep_logged_in': True
        }
    )
    
    with app.app_context():
        assert User.query.count() == 1

def test_signup_cpf_exists(client, app):
    response = client.post(
        '/sign-up',
        data={
            'email': 'test@test.com',
            'password': 'test1234',
            'password_check': 'test1234',
            'full_name': 'Tester',
            'birth_date': datetime.strptime('01/01/2000', '%d/%m/%Y'),
            'cpf': '539.529.150-41', # Aleatório
            'keep_logged_in': True
        }
    )
    
    with app.app_context():
        assert User.query.filter_by(email='test@test.com').first().cpf == '539.529.150-41'
    
    response = client.post(
        '/sign-up',
        data={
            'email': 'test1@test.com',
            'password': 'test1234',
            'password_check': 'test1234',
            'full_name': 'Tester',
            'birth_date': datetime.strptime('01/01/2000', '%d/%m/%Y'),
            'cpf': '539.529.150-41', # Aleatório
            'keep_logged_in': True
        }
    )
    
    with app.app_context():
        assert User.query.count() == 1

def test_validate_cpf():
    assert validate_cpf('199.743.100-91')
    assert not validate_cpf('111.111.111-11')

def test_signup_invalid_cpf(client, app):
    client.post(
        '/sign-up',
        data={
            'email': 'test1@test.com',
            'password': 'test1234',
            'password_check': 'test1234',
            'full_name': 'Tester',
            'birth_date': datetime.strptime('01/01/2000', '%d/%m/%Y'),
            'cpf': '111.111.111-11', # Aleatório
            'keep_logged_in': True
        }
    )
    
    with app.app_context():
        assert User.query.count() == 0

def test_signup_invalid_email(client, app):
    client.post(
        '/sign-up',
        data={
            'email': 'test1test.com',
            'password': 'test1234',
            'password_check': 'test1234',
            'full_name': 'Tester',
            'birth_date': datetime.strptime('01/01/2000', '%d/%m/%Y'),
            'cpf': '111.111.111-11', # Aleatório
            'keep_logged_in': True
        }
    )
    
    with app.app_context():
        assert User.query.count() == 0

def test_signup_different_passwords(client, app):
    client.post(
        '/sign-up',
        data={
            'email': 'test1@test.com',
            'password': 'test1234',
            'password_check': '----',
            'full_name': 'Tester',
            'birth_date': datetime.strptime('01/01/2000', '%d/%m/%Y'),
            'cpf': '111.111.111-11', # Aleatório
            'keep_logged_in': True
        }
    )
    
    with app.app_context():
        assert User.query.count() == 0

def test_signup_invalid_birth_date(client, app):
    response = client.post(
        '/sign-up',
        data={
            'email': 'test1@test.com',
            'password': 'test1234',
            'password_check': 'test1234',
            'full_name': 'Tester',
            'birth_date': datetime.strftime(datetime.now(), '%Y-%m-%d'),
            'cpf': '111.111.111-11', # Aleatório
            'keep_logged_in': True
        }
    )
    
    with app.app_context():
        assert User.query.count() == 0

def test_email_login(client, app):
    client.post(
        '/sign-up',
        data={
            'email': 'test1@test.com',
            'password': 'test1234',
            'password_check': 'test1234',
            'full_name': 'Tester',
            'birth_date': datetime.strftime(datetime.now(), '%Y-%m-%d'),
            'cpf': '111.111.111-11', # Aleatório
            'keep_logged_in': True
        }
    )
    
    response = client.get('/checked_in')
    
    assert b'<!doctype html>' in response.data
    
    response = client.post('logout')
    
    assert b'<!doctype html>' in response.data
    
    response = client.post(
        '/login',
        data = {
            'id_method': 'test1@test.com',
            'password': 'test1234',
            'keep_logged_in': True
        }
    )
    
    assert b'<!doctype html>' in response.data

def test_cpf_login(client, app):
    client.post(
        '/sign-up',
        data={
            'email': 'test1@test.com',
            'password': 'test1234',
            'password_check': 'test1234',
            'full_name': 'Tester',
            'birth_date': datetime.strftime(datetime.now(), '%Y-%m-%d'),
            'cpf': '111.111.111-11', # Aleatório
            'keep_logged_in': True
        }
    )
    
    client.post(
        '/login',
        data = {
            'id_method': '111.111.111-11',
            'password': 'test1234',
            'keep_logged_in': True
        }
    )
    
    with app.app_context():
        assert checked_in()

def test_login_after_signup(client, app):
    client.post(
        '/sign-up',
        data={
            'email': 'test1@test.com',
            'password': 'test1234',
            'password_check': 'test1234',
            'full_name': 'Tester',
            'birth_date': datetime.strftime(datetime.now(), '%Y-%m-%d'),
            'cpf': '111.111.111-11', # Aleatório
            'keep_logged_in': True
        }
    )
    
    with app.app_context():
        assert checked_in()

def test_invalid_login(client, app):
    client.post(
        '/login',
        data={
            'id_method': 'test1@test.com',
            'password': 'test1234',
            'keep_logged_in': True
        }
    )
    
    with app.app_context():
        assert not checked_in()

def test_logout(client, app):
    client.post(
        '/sign-up',
        data={
            'email': 'test1@test.com',
            'password': 'test1234',
            'password_check': 'test1234',
            'full_name': 'Tester',
            'birth_date': datetime.strftime(datetime.now(), '%Y-%m-%d'),
            'cpf': '111.111.111-11', # Aleatório
            'keep_logged_in': True
        }
    )
    
    with app.app_context():
        assert checked_in()
    
    client.get(
        '/logout'
    )
    
    with app.app_context():
        assert not checked_in()