from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/')
def home(): #Quem for fazer a home, pode deixar aqui
    return "<h1>Test</h1>"