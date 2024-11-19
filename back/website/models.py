from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(150), unique=True)
    cpf = db.Column(db.String(11), nullable=True, unique=True)
    password = db.Column(db.String(150), nullable=True)
    full_name = db.Column(db.String(150))
    data_nasc = db.Column(db.DateTime(timezone=True), nullable=True)
    data_criacao = db.Column(db.DateTime(timezone=True), default=datetime.now())
    google_linked = db.Column(db.Integer, nullable=False, default=0)
    
    def set_password(self, password: str):
        self.password = generate_password_hash(password)
    
    def check_password(self, password_to_check):
        return check_password_hash(self.password, password_to_check)

class CursosEmProgresso(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey("curso.id"), primary_key=True)
    progresso = db.Column(db.Integer)
    data_final = db.Column(db.DateTime(timezone=True))

class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), unique=True)
    descricao = db.Column(db.String(3600))
    horas_estimado = db.Column(db.Integer)
    texto_certificado = db.Column(db.String(3600))
    questionario_id = db.Column(db.Integer, db.ForeignKey("questionario.id"))

class Questionario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pontos_min = db.Column(db.Integer)
    pontos_max = db.Column(db.Integer)
    minutos_max = db.Column(db.Integer)

class Ementa(db.Model):
    aula_id = db.Column(db.Integer, db.ForeignKey("aula.id"), primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey("curso.id"), primary_key=True)

class Aula(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(150))

class VideoAula(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(150))
    minutos_duracao = db.Column(db.Integer)
    segundos_duracao = db.Column(db.Integer)
    titulo = db.Column(db.String(150))
    aula_id = db.Column(db.Integer, db.ForeignKey("aula.id"))

class AcervoDeQuestoes(db.Model):
    questionario_id = db.Column(db.Integer, db.ForeignKey("aula.id"), primary_key=True)
    questao_id = db.Column(db.Integer, db.ForeignKey("curso.id"), primary_key=True)
    valor_pontos_questao = db.Column(db.Integer)

class Questao(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enunciado = db.Column(db.String(3600))
    alternativa_A = db.Column(db.String(3600))
    alternativa_B = db.Column(db.String(3600))
    alternativa_C = db.Column(db.String(3600))
    alternativa_D = db.Column(db.String(3600))
    alternativa_E = db.Column(db.String(3600))
    resposta_correta = db.Column(db.String(1))

class RespostaAoQuestionario(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    questionario_id = db.Column(db.Integer, db.ForeignKey("questionario.id"), primary_key=True)
    pontuacao = db.Column(db.Integer)
    data_realizacao = db.Column(db.DateTime(timezone=True))