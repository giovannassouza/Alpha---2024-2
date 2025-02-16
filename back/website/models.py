from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import Response
from .json_responses import successful_response, error_response

# Models:
#   User, 
#   Curso, 
#   Questionario, 
#   Aula, 
#   AcervoDeQuestoes, 
#   Questao, 
#   RespostaAoQuestionario, 
#   Assinaturas

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(300), unique=True)
    cpf = db.Column(db.String(15), nullable=True, unique=True)
    password = db.Column(db.String(150), nullable=True)
    full_name = db.Column(db.String(200))
    data_nasc = db.Column(db.DateTime(timezone=True), nullable=True)
    data_criacao = db.Column(db.DateTime(timezone=True), default=datetime.now())
    cliente_tina = db.Column(db.Integer, nullable=False, default=0)
    assinante   = db.Column(db.Integer, nullable=True, default=0)
    is_active = db.Column(db.Integer, nullable=False, default=1)
    is_adm = db.Column(db.Integer, nullable=False, default=0)
    email_authenticated = db.Column(db.Integer, default=0)
    email_authentication_code = db.Column(db.String(7), nullable=True, default=None)
    
    def is_adm(self) -> bool:
        return True if self.is_adm == 1 else False
    
    def set_password(self, password: str) -> str:
        self.password = generate_password_hash(password)
    
    def check_password(self, password_to_check) -> bool:
        return check_password_hash(self.password, password_to_check)
    
    def check_signature(self) -> Response:
        signature = Assinaturas.query.filter_by(user_id= self.id).first()
        if not signature:
            return error_response(description="Subscription not found in database.", response=401)
        if not signature.fim:
            return successful_response(description="Subscription not found in database.", data={"fim_assinatura": None, "answer": 401})
        if signature.fim < datetime.now():
            self.assinante = 0
            db.session.commit()
            return successful_response(description="Subscription expired.", data={"fim_assinatura": signature.fim, "answer": 401})
        else:
            self.assinante = 1
            db.session.commit()
            return successful_response(description="Subscription successfully validated.", data={"fim_assinatura": signature.fim, "answer": 200})

class CursosEmProgresso(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey("curso.id"), primary_key=True)
    progresso = db.Column(db.Integer)
    data_final = db.Column(db.DateTime(timezone=True))

class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), unique=True)
    descricao = db.Column(db.Text)
    nAulas = db.Column(db.Integer)
    image_file = db.Column(db.LargeBinary, default=None, nullable=True)
    image_file_name = db.Column(db.String(300), default=None, nullable=True)

class Questionario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    q1 = db.Column(db.Integer, db.ForeignKey("questao.id"))
    q2 = db.Column(db.Integer, db.ForeignKey("questao.id"))
    q3 = db.Column(db.Integer, db.ForeignKey("questao.id"))
    q4 = db.Column(db.Integer, db.ForeignKey("questao.id"))
    q5 = db.Column(db.Integer, db.ForeignKey("questao.id"))
    pontos_min = db.Column(db.Integer)
    pontos_max = db.Column(db.Integer)
    minutos_max = db.Column(db.Integer)

class Aula(db.Model):
    curso_id = db.Column(db.Integer, db.ForeignKey("curso.id"))
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(150))
    titulo = db.Column(db.String(150))
    descricao = db.Column(db.Text)

class AcervoDeQuestoes(db.Model):
    questionario_id = db.Column(db.Integer, db.ForeignKey("aula.id"), primary_key=True)
    questao_id = db.Column(db.Integer, db.ForeignKey("curso.id"), primary_key=True)
    valor_pontos_questao = db.Column(db.Integer)

class Questao(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_curso = db.Column(db.Integer, db.ForeignKey("curso.id"))
    enunciado = db.Column(db.Text)
    alternativa_A = db.Column(db.Text)
    alternativa_B = db.Column(db.Text)
    alternativa_C = db.Column(db.Text)
    alternativa_D = db.Column(db.Text)
    alternativa_E = db.Column(db.Text)
    resposta_correta = db.Column(db.String(1))

class RespostaAoQuestionario(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    questionario_id = db.Column(db.Integer, db.ForeignKey("questionario.id"), primary_key=True)
    pontuacao = db.Column(db.Integer)
    data_realizacao = db.Column(db.DateTime(timezone=True))

class Assinaturas(db.Model):
    assinatura_id   = db.Column(db.Integer, primary_key=True, autoincrement="ignore_fk")
    user_id         = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    inicio          = db.Column(db.DateTime(timezone=True), nullable=True)
    fim             = db.Column(db.DateTime(timezone=True), nullable=True)
    TipoAssinatura  = db.Column(db.Integer, nullable = True)
