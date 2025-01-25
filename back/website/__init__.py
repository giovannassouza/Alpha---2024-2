from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from os import path
from authlib.integrations.flask_client import OAuth
from .api_key import APP_SECRET, USER, PASSWORD, HOST, PORT, DB_NAME, CLIENT_SECRET, CLIENT_ID, FRONT_END_URLS
from flask_login import LoginManager
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
oauth = OAuth()
google = oauth.register(
    name = 'google',
    client_id = 'CLIENT_ID',
    client_secret = 'CLIENT_SECRET',
    #server_metadata_uri='http://metadata.google.internal/computeMetadata/v1',
    access_token_url = 'https://account.google.com/o/oauth2/token',
    access_token_params = None,
    authorize_url = 'https://accounts.google.com/o/oauth2/auth',
    authorize_params = None,
    api_base_url = 'https://www.googleapis.com/oauth2/v1/',
    client_kwargs = {'scope': 'openid profile email'}
)
csrf = CSRFProtect()
swagger = Swagger()

def create_app():
    # Flask app setup
    app = Flask(__name__)
    app.config['SECRET_KEY'] = APP_SECRET
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
    
    # Documentation setup
    swagger.init_app(app)
    app.config['SWAGGER'] = {
        'title': 'Tina: Gestão de Cantinas - API Documentation',
        'uiversion': 3
    }
    
    # Login protection setup
    csrf.init_app(app)
    app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken']
    
    # CORS setup
    CORS(app, resources={r"/*": {"origins": FRONT_END_URLS}})
    
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
    
    # Initialize OAuth
    oauth.init_app(app) # create authentication instance attached to app
    
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

