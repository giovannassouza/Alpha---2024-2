from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from os import path
from .api_key import *
from flask_login import LoginManager
from flask_cors import CORS

app_url = "127.0.0.1:5000"
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
    CORS(app, supports_credentials=True, origins=front_urls)

    
    # Login manager setup
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    from .views import views
    from .auth import auth
    from .payment import payment
    from .quiz import quiz
    from .certificate import certificate
    from .wtf_error import wtf_error
    from .account_management import account_management
    from .utils import utils
    
    
    # Initialize the database with the app
    db.init_app(app)
    
    # Imports classes from models
    from .models import User, CursosEmProgresso, Curso, Questionario, Questao, Ementa, Aula#, VideoAula, AcervoDeQuestoes, RespostaAoQuestionario
    
    # creates database
    create_database(app)
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(payment, url_prefix='/')
    app.register_blueprint(quiz, url_prefix='/')
    app.register_blueprint(certificate, url_prefix='/')
    app.register_blueprint(wtf_error, url_prefix='/')
    app.register_blueprint(account_management, url_prefix='/')
    app.register_blueprint(utils, url_prefix='/')
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
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

