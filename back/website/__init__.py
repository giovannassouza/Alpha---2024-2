from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from authlib.integrations.flask_client import OAuth
# from flask_login import LoginManager 

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'OUR-PLATINA' #da pra mudar tbm nao é definitivo e tbm não é tãaao importante assim
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"

    from .views import views
    from .auth import auth
    from .payment import payment
    
    # Initialize OAuth
    oauth = OAuth(app)

    # Initialize the database with the app
    db.init_app(app)

    # Imports classes from models
    from .models import User, CursosEmProgresso, Curso, Questionario, Questao, Ementa, Aula, VideoAula, AcervoDeQuestoes, RespostaAoQuestionario
    
    # creates database
    create_database(app)

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(payment, url_prefix='/')

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created Database!')

