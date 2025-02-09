from flask import Flask, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from .models import Curso, Questao, Aula,AcervoDeQuestoes
pull = Blueprint('pull', __name__)

@pull.route('/courses', methods=['GET'])
def get_courses():
    courses = Curso.query.all()
    print(courses)
    return jsonify([{'id': course.id, 'name': course.nome, 'description': course.descricao} for course in courses])

@pull.route('/classes/<int:course_id>', methods=['GET'])
def get_classes(course_id):
    classes = Aula.query.filter_by(curso_id=course_id).all()
    return jsonify([{'id': class_.id, 'title': class_.titulo, 'description': class_.descricao, 'url': class_.url} for class_ in classes])

@pull.route('/acervo-questoes', methods=['GET'])
def get_acervo_questoes():
    # Consulta todos os registros da tabela AcervoDeQuestoes
    acervo_questoes = AcervoDeQuestoes.query.all()

    # Converte os resultados para uma lista de dicionários
    acervo_list = [{
        'questionario_id': acervo.questionario_id,
        'questao_id': acervo.questao_id,
        'valor_pontos_questao': acervo.valor_pontos_questao
    } for acervo in acervo_questoes]

    # Retorna os dados em formato JSON
    return jsonify(acervo_list)


@pull.route('/questions/<int:course_id>', methods=['GET'])
def get_questions(course_id):
    questions = Questao.query.filter_by(id_curso=course_id).all()
    return jsonify([{
        'id': question.id,
        'statement': question.enunciado,
        'options': {
            'A': question.alternativa_A,
            'B': question.alternativa_B,
            'C': question.alternativa_C,
            'D': question.alternativa_D,
            'E': question.alternativa_E
        },
        'correct_answer': question.resposta_correta
    } for question in questions])
