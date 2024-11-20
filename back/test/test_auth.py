from website.models import User
from website.auth import create_user, sign_up
import datetime
import responses

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

#def test_signup_fail():