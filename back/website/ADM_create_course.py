from flask import Flask, flash, render_template, request, redirect, url_for, Blueprint, jsonify
from sqlalchemy import text
from flask_login import login_required
import base64
from io import BytesIO

from .json_responses import error_response, successful_response
from .models import Curso, Aula, Questao
from . import db

cc = Blueprint('course_creation', __name__)


# Rota para processar o JSON
@cc.route('/criar_curso', methods=['POST', 'GET'])
def criar_curso():
    """
    Endpoint to create a new course.
    ---
    tags:
      - Courses
    parameters:
      - name: titulo
        in: body
        type: string
        required: true
        description: The title of the course.
      - name: numero_aulas
        in: body
        type: int
        required: true
        description: The number of classes in the course.
      - name: descricao_curso
        in: body
        type: string
        required: true
        description: The description of the course.
      - name: imagem_curso
        in: body
        type: string
        required: false
        description: Base64-encoded image of the course.
      - name: aulas
        in: body
        type: array
        items:
          type: object
          properties:
            titulo:
              type: string
              description: The title of the class.
            descricao:
              type: string
              description: The description of the class.
            url:
              type: string
              description: The URL of the class.
      - name: questoes
        in: body
        type: array
        items:
          type: object
          properties:
            enunciado:
              type: string
              description: The statement of the question.
            alternativa_a:
              type: string
              description: Option A of the question.
            alternativa_b:
              type: string
              description: Option B of the question.
            alternativa_c:
              type: string
              description: Option C of the question.
            alternativa_d:
              type: string
              description: Option D of the question.
            alternativa_e:
              type: string
              description: Option E of the question.
            resposta_correta:
              type: string
              description: The correct answer to the question.
    responses:
      200:
        description: Course created successfully.
      400:
        description: Bad request. No JSON data provided.
      500:
        description: Internal server error. Could not create course or add class/question.
    """
    if request.method == 'POST':
        # Parse JSON data
        data = request.get_json()

        if not data:
            return error_response(description="No JSON data provided.", response=400)

        try:
            # Extract course data from JSON
            course_name = data.get('titulo')
            nAulas = data.get('numero_aulas')
            course_description = data.get('descricao_curso')
            course_image_base64 = data.get('imagem_curso')  # Base64-encoded image

            # Decode the base64 image (if provided)
            if course_image_base64:
                course_image_data = base64.b64decode(course_image_base64)
                course_image_file_name = f"{course_name}_image.jpg"  # Generate a filename
            else:
                course_image_data = None
                course_image_file_name = None

            # Create the course
            course = Curso(nome=course_name, descricao=course_description, nAulas=nAulas, image_file=course_image_data, image_file_name=course_image_file_name)
            db.session.add(course)
            db.session.flush()  # Ensure the course ID is generated
        except Exception as e:
            db.session.rollback()
            return error_response(description="Internal Server Error. Could not create course", response=500, error_details={"exception": str(e)})
        try:
                # Insert aulas
                aulas = data.get('aulas', [])
                for aula in aulas:
                    sentence1 = text('''
                    INSERT INTO Aula (curso_id, titulo, descricao, url)
                    VALUES (:curso_id, :titulo, :descricao, :url)
                    ''')
                    db.session.execute(sentence1, {
                        'curso_id': course.id,
                        'titulo': aula.get('titulo'),
                        'descricao': aula.get('descricao'),
                        'url': aula.get('url')
                    })
        except Exception as e:
            db.session.rollback()
            return error_response(description="Internal Server Error. Could not add class", response=500, error_details={"exception": str(e)})
        try:
            # Insert questões
            questoes = data.get('questoes', [])
            for questao in questoes:
                query = '''
                INSERT INTO Questao (id_curso, enunciado, alternativa_A, alternativa_B, alternativa_C, alternativa_D, alternativa_E, resposta_correta)
                VALUES (:id_curso, :enunciado, :alternativa_a, :alternativa_b, :alternativa_c, :alternativa_d, :alternativa_e, :resposta_correta)
                '''
                params = {
                    'id_curso': course.id,
                    'enunciado': questao.get('enunciado'),
                    'alternativa_a': questao.get('alternativa_a'),
                    'alternativa_b': questao.get('alternativa_b'),
                    'alternativa_c': questao.get('alternativa_c'),
                    'alternativa_d': questao.get('alternativa_d'),
                    'alternativa_e': questao.get('alternativa_e'),
                    'resposta_correta': questao.get('resposta_correta')
                }
                sentence2 = text(query)
                db.session.execute(sentence2, params)

            # Commit changes to the database
            db.session.commit()
            return successful_response(description="Created course", response=200)

        except Exception as e:
            db.session.rollback()
            return error_response(description="Internal Server Error. Could not add question", response=500, error_details={"exception": str(e)})

    return render_template("ADM_create_course_template.html")