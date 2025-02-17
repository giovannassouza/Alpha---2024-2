from flask import Flask, jsonify, Blueprint, request
from flask_sqlalchemy import SQLAlchemy
from .models import Curso, Questao, Aula, AcervoDeQuestoes, CursosEmProgresso
from .json_responses import successful_response, error_response
from . import db

manage_courses = Blueprint('manage_courses', __name__)

@manage_courses.route('/courses/update-progress', methods=['POST'])
def update_course_progress():
    """
    Endpoint to update the progress of a user in a course.
    ---
    tags:
      - Courses
    parameters:
      - name: user_id
        in: body
        type: int
        required: true
        description: The ID of the user.
      - name: course_id
        in: body
        type: int
        required: true
        description: The ID of the course.
      - name: progress
        in: body
        type: int
        required: true
        description: The progress of the user in the course.
    responses:
      200:
        description: Progress updated successfully.
      400:
        description: Bad request. Missing required parameters.
      500:
        description: Internal server error. Could not update progress.
    """
    data = request.get_json()
    user_id = data.get('user_id')
    course_id = data.get('course_id')
    progress = data.get('progress')

    if not user_id or not course_id or not progress:
        return error_response(description='Missing required parameters', response=400)

    try:
        curso_em_progresso = CursosEmProgresso.query.filter_by(user_id=user_id, curso_id=course_id).first()
        if curso_em_progresso:
            curso_em_progresso.progresso = progress
            db.session.commit()
            return successful_response(description='Progress updated successfully')
        else:
            return error_response(description='Course progress not found', response=404)
    except Exception as e:
        db.session.rollback()
        return error_response(description='Internal server error', response=500, error_details={"exception": str(e)})

@manage_courses.route('/courses/create-relation', methods=['POST'])
def create_course_relation():
    """
    Endpoint to create a relation in CursosEmProgresso.
    ---
    tags:
      - Courses
    parameters:
      - name: user_id
        in: body
        type: int
        required: true
        description: The ID of the user.
      - name: course_id
        in: body
        type: int
        required: true
        description: The ID of the course.
    responses:
      200:
        description: Relation created successfully.
      400:
        description: Bad request. Missing required parameters.
      500:
        description: Internal server error. Could not create relation.
    """
    data = request.get_json()
    user_id = data.get('user_id')
    course_id = data.get('course_id')
    
    if not user_id or not course_id:
        return error_response(description='Missing required parameters', response=400)
    
    try:
        new_relation = CursosEmProgresso(user_id=user_id, curso_id=course_id, progresso=0)
        db.session.add(new_relation)
        db.session.commit()
        return successful_response(description='Relation created successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(description='Internal server error', response=500, error_details={"exception": str(e)})

