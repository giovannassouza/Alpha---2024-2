from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from os import path
from .api_key import *
from flask_login import LoginManager
from flask_cors import CORS

app_url = "http://127.0.0.1:8080"
db = SQLAlchemy()
swagger = Swagger()

def create_app():
    # Flask app setup
    app = Flask(__name__)
    app.config['SECRET_KEY'] = APP_SECRET
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    # Documentation setup
    swagger.init_app(app)
    app.config['SWAGGER'] = {
        'title': 'Tina: Gestão de Cantinas - API Documentation',
        'uiversion': 3
    }
    
    # CORS setup
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True
    CORS(app, supports_credentials=True, origins=FRONT_URLS)
    
    # Login manager setup
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    

    from .auth import auth
    from .payment import payment
    from .quiz import quiz
    from .certificate import certificate
    from .account_management import account_management
    from .utils import utils
    from .ADM_create_course import cc
    from .pull_courses import pull
    from .youtube import youtube
    
    # Initialize the database with the app
    db.init_app(app)
    
    # Imports classes from models
    from .models import User, CursosEmProgresso, Curso, Questionario, Questao, Aula, AcervoDeQuestoes, Assinaturas
    
    # creates database
    create_database(app)
    
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(payment, url_prefix='/')
    app.register_blueprint(quiz, url_prefix='/')
    app.register_blueprint(certificate, url_prefix='/')
    app.register_blueprint(account_management, url_prefix='/')
    app.register_blueprint(utils, url_prefix='/')
    app.register_blueprint(cc, url_prefix='/')
    app.register_blueprint(pull, url_prefix='/')
    app.register_blueprint(youtube, url_prefix='/')
    
    from . import models
    @login_manager.user_loader
    def load_user(id):
        # Return the user object for the given user_id
        return models.User.query.get(int(id))
    
    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created Database!')
            add_debug_data()

def add_debug_data():
    # Add debug data to the database
    from .models import User, Curso, Aula, Questao, Questionario, AcervoDeQuestoes, Assinaturas
    from .utils import create_user
    from datetime import datetime, timedelta

    if User.query.count() > 0:
        return
    # Create users
    user1 = create_user(
        email="es.grupoalpha2024@gmail.com",
        full_name="[ADM USER]",
        cpf="269.851.170-23",
        password="admin",
        data_nasc=datetime(1992, 2, 2),
        is_adm=0,
        cliente_tina=True
    )
    user2 = create_user(
        email="user2@example.com",
        full_name="User Two",
        cpf="609.688.090-81",
        password="password2",
        data_nasc=datetime(1992, 2, 2),
        cliente_tina=True
    )

    if Curso.query.count() > 0:
        return
    # Create courses
    curso1 = Curso(
        nome="Curso de Marketing", 
        descricao="Aprenda marketing para restaurantes", 
        nAulas=10
        )
    curso2 = Curso(
        nome="Curso de Finanças", 
        descricao="Aprenda finanças para restaurantes", 
        nAulas=8
        )
    db.session.add(curso1)
    db.session.add(curso2)
    db.session.commit()

    if Aula.query.count() > 0:
        return
    # Create classes
    aula1 = Aula(curso_id=curso1.id, url="http://example.com/aula1", titulo="Introdução ao Marketing", descricao="Aula introdutória de marketing")
    aula2 = Aula(curso_id=curso1.id, url="http://example.com/aula2", titulo="Marketing Digital", descricao="Aula sobre marketing digital")
    aula3 = Aula(curso_id=curso2.id, url="http://example.com/aula3", titulo="Introdução às Finanças", descricao="Aula introdutória de finanças")
    db.session.add(aula1)
    db.session.add(aula2)
    db.session.add(aula3)
    db.session.commit()

    if Questao.query.count() > 0:
        return
    # Create questions
    questao1 = Questao(
        id_curso=curso1.id, 
        enunciado="O que é marketing?", 
            alternativa_A="Opção A", 
            alternativa_B="Opção B", 
            alternativa_C="Opção C", 
            alternativa_D="Opção D", 
            alternativa_E="Opção E", 
        resposta_correta="A")
    questao2 = Questao(
        id_curso=curso2.id,
        enunciado="O que é finanças?", 
            alternativa_A="Opção A", 
            alternativa_B="Opção B", 
            alternativa_C="Opção C", 
            alternativa_D="Opção D", 
            alternativa_E="Opção E", 
        resposta_correta="B"
        )
    db.session.add(questao1)
    db.session.add(questao2)
    db.session.commit()

    if Questionario.query.count() > 0:
        return
    # Create questionnaires
    questionario1 = Questionario(q1=questao1.id, q2=questao2.id, pontos_min=5, pontos_max=10, minutos_max=30)
    db.session.add(questionario1)
    db.session.commit()

    if AcervoDeQuestoes.query.count() > 0:
        return
    # Create question archive
    acervo1 = AcervoDeQuestoes(questionario_id=questionario1.id, questao_id=questao1.id, valor_pontos_questao=5)
    acervo2 = AcervoDeQuestoes(questionario_id=questionario1.id, questao_id=questao2.id, valor_pontos_questao=5)
    db.session.add(acervo1)
    db.session.add(acervo2)
    db.session.commit()

    if Assinaturas.query.count() > 0:
        return
    # Create subscriptions
    assinatura1 = Assinaturas(user_id=user1.id, inicio=datetime.now(), fim=datetime.now() + timedelta(days=365), TipoAssinatura=1)
    assinatura2 = Assinaturas(user_id=user2.id, inicio=datetime.now(), fim=datetime.now() + timedelta(days=365), TipoAssinatura=2)
    db.session.add(assinatura1)
    db.session.add(assinatura2)
    db.session.commit()

    print('Added debug data to the database.')

