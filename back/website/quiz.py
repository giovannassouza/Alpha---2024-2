from flask import Blueprint, request, render_template

from .models import *
from website.models import *
from datetime import datetime

quiz = Blueprint('quiz',__name__)

@quiz.route('/quiz/forms', methods = ['GET','POST'])
def quizWrite():
    if(request.method == 'POST'):
        enunciado = request.form.get('enunciado')
        alternativa_A = request.form.get('alternativa_A')
        alternativa_B = request.form.get('alternativa_B')
        alternativa_C = request.form.get('alternativa_C')
        alternativa_D = request.form.get('alternativa_D')
        alternativa_E = request.form.get('alternativa_E')
        resposta_correta = request.form.get('resposta_correta')
        question = Questao(enunciado = enunciado, alternativa_A = alternativa_A, alternativa_B = alternativa_B, alternativa_C = alternativa_C, alternativa_D = alternativa_D, alternativa_E = alternativa_E, resposta_correta=resposta_correta)
        db.session.add(question)
        db.session.commit()
    return render_template('new_question_form.html')

@quiz.route('/quiz', methods = ['GET'])
def quizRead():
    try:
        questionario = db.session.execute(db.select(Questionario).filter_by(id = 1)).scalar_one()

        questionIdFromQuestionario = [questionario.q1, questionario.q2, questionario.q3, questionario.q4, questionario.q5]
        qText = ""
        for question in questionIdFromQuestionario:
            qX = db.session.execute(db.select(Questao).filter_by(id = question)).scalar_one()
            qText += qX.enunciado + '<ul>'
            qText += '<li>' + qX.alternativa_A + '</li>'
            qText += '<li>' + qX.alternativa_B + '</li>'
            qText += '<li>' + qX.alternativa_C + '</li>'
            qText += '<li>' + qX.alternativa_D + '</li>'
            qText += '<li>' + qX.alternativa_E + '</li>'
            qText += '<li>' + qX.resposta_correta + '</li>'
            qText += '</ul>'
        return qText
    
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text
