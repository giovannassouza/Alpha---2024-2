from flask import Flask, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
<<<<<<< HEAD
from .models import Curso, Questao, Aula,AcervoDeQuestoes
=======
from .models import Curso, Questao, Aula, AcervoDeQuestoes
from .json_responses import successful_response, error_response

>>>>>>> a24c8f6a6d3f45f1ad26f895801c3ba495a51fa8
pull = Blueprint('pull', __name__)

@pull.route('/courses', methods=['GET'])
def get_courses():
<<<<<<< HEAD
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
=======
    """
    Retrieve all courses.
    ---
    tags:
      - Courses
    responses:
      200:
        description: A list of courses.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              description:
                type: string
    """
    try:
        courses = Curso.query.all()
        return successful_response(
            description="Courses retrieved successfully",
            data=[{'id': course.id, 'name': course.nome, 'description': course.descricao} for course in courses]
        )
    except Exception as e:
        return error_response(description=str(e))

@pull.route('/classes/<int:course_id>', methods=['GET'])
def get_classes(course_id):
    """
    Retrieve all classes for a specific course.
    ---
    tags:
      - Classes
    parameters:
      - name: course_id
        in: path
        type: integer
        required: true
        description: The ID of the course.
    responses:
      200:
        description: A list of classes.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              description:
                type: string
              url:
                type: string
    """
    try:
        classes = Aula.query.filter_by(curso_id=course_id).all()
        return successful_response(
            description="Classes retrieved successfully",
            data=[{'id': class_.id, 'title': class_.titulo, 'description': class_.descricao, 'url': class_.url} for class_ in classes]
        )
    except Exception as e:
        return error_response(description=str(e))

@pull.route('/acervo-questoes', methods=['GET'])
def get_acervo_questoes():
    """
    Retrieve all records from AcervoDeQuestoes.
    ---
    tags:
      - AcervoDeQuestoes
    responses:
      200:
        description: A list of acervo questoes.
        schema:
          type: array
          items:
            type: object
            properties:
              questionario_id:
                type: integer
              questao_id:
                type: integer
              valor_pontos_questao:
                type: number
    """
    try:
        acervo_questoes = AcervoDeQuestoes.query.all()
        acervo_list = [{
            'questionario_id': acervo.questionario_id,
            'questao_id': acervo.questao_id,
            'valor_pontos_questao': acervo.valor_pontos_questao
        } for acervo in acervo_questoes]
        return successful_response(
            description="Acervo de Questoes retrieved successfully",
            data=acervo_list
        )
    except Exception as e:
        return error_response(description.str(e))

@pull.route('/questions/<int:course_id>', methods=['GET'])
def get_questions(course_id):
    """
    Retrieve all questions for a specific course.
    ---
    tags:
      - Questions
    parameters:
      - name: course_id
        in: path
        type: integer
        required: true
        description: The ID of the course.
    responses:
      200:
        description: A list of questions.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              statement:
                type: string
              options:
                type: object
                properties:
                  A:
                    type: string
                  B:
                    type: string
                  C:
                    type: string
                  D:
                    type: string
                  E:
                    type: string
              correct_answer:
                type: string
    """
    try:
        questions = Questao.query.filter_by(id_curso=course_id).all()
        return successful_response(
            description="Questions retrieved successfully",
            data=[{
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
            } for question in questions]
        )
    except Exception as e:
        return error_response(description=str(e))
>>>>>>> a24c8f6a6d3f45f1ad26f895801c3ba495a51fa8
