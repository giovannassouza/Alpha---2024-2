from flask import Flask, flash, render_template, request, redirect, url_for, Blueprint
from sqlalchemy import text
from flask_login import login_required
import mysql.connector

from .json_responses import error_response, successful_response
from .models import Curso, Aula, Questao
from . import db

cc = Blueprint('course_creation',__name__)


# Rota para processar o formulário
@cc.route('/criar_curso', methods=['POST', 'GET'])
@login_required
def criar_curso():
    if(request.method == 'POST'):
        # Inserir dados do curso
        try:
            course_name = request.form['titulo']
            nAulas = request.form['numero_aulas']
            course_description = request.form['descricao_curso']
            #RESOLVER IMAGENS DEPOIS
            course_image_file_name = request.files['imagem_curso'].filename  # Nome do arquivo da imagem
            course = Curso(nome = course_name, descricao = course_description, image_URL = course_image_file_name,nAulas=nAulas)
            db.session.add(course)
        except Exception as e:
            return error_response(description="Bad Gateway.", response=502, error_details={"exception": "received an invalid response from an upstream server."})

        # Inserir aulas
        for i in range(1, int(request.form['numero_aulas']) + 1):
            sentence1 = text('''
            INSERT INTO Aula (curso_id, titulo, descricao, url)
            VALUES (:curso_id, :titulo, :descricao, :url)
            ''')
    # Executar a consulta com os parâmetros
            db.session.execute(sentence1, {
                'curso_id': course.id,
                'titulo': request.form.get(f'titulo_aula_{i}'),
                'descricao': request.form.get(f'descricao_aula_{i}'),
                'url': request.form.get(f'url_aula_{i}')
            })
        # Inserir questões e alternativas
        for i in range(1, 6):  # Até 5 questões
            enunciado = request.form.get(f'enunciado_questao_{i}')
            try:
                if enunciado:
                    query = '''
                    INSERT INTO Questao (id_curso, enunciado, alternativa_A, alternativa_B, alternativa_C, alternativa_D, alternativa_E, resposta_correta)
                    VALUES (:id_curso, :enunciado, :alternativa_a, :alternativa_b, :alternativa_c, :alternativa_d, :alternativa_e, :resposta_correta)
                    '''
                    # Parâmetros em um dicionário
                    params = {
                        'id_curso': course.id,
                        'enunciado': enunciado,
                        'alternativa_a': request.form.get(f'alternativa_a_{i}'),
                        'alternativa_b': request.form.get(f'alternativa_b_{i}'),
                        'alternativa_c': request.form.get(f'alternativa_c_{i}'),
                        'alternativa_d': request.form.get(f'alternativa_d_{i}'),
                        'alternativa_e': request.form.get(f'alternativa_e_{i}'),
                        'resposta_correta': request.form.get(f'resposta_questao_{i}')
                    }
                    # Executar a consulta com o SQLAlchemy
                    sentence2 = text(query)
                    db.session.execute(sentence2, params)
            except Exception as e:
                return error_response(description="Bad Gateway.", response=502, error_details={"exception": "received an invalid response from an upstream server."})
        # Salvar e fechar a conexão
        db.session.commit()
        db.session.close()
        return successful_response(description="Created course", response=200)

    return render_template("ADM_create_course_template.html")