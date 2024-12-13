import os
from flask import Blueprint, Flask, render_template, send_file, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .certificate_api import gerar_certificado_pdf
from .models import *
from website.models import *

certificate = Blueprint('certificate', __name__)

@certificate.route('/class/certificate', methods=['GET'])
@login_required
def get_certificate():
    try:
        user_id = current_user.get_id()

        query = db.select(CursosEmProgresso.curso_id).where(
             (CursosEmProgresso.user_id == user_id) & (CursosEmProgresso.progresso >95))
        cursosFeitos = db.session.execute(db.select(Curso).where(Curso.id.in_(query))).scalars().all()

        user_data = db.session.execute(db.select(User).where(User.id == user_id)).scalar_one()

        download_urls = []
        for curso in cursosFeitos:
                    filename = secure_filename(f"certificado_{curso.nome}.pdf")
                    file_path = gerar_certificado_pdf(
                        user_data.full_name,
                        curso.nome,
                        curso.horas_estimado,
                        caminho_certificado=f'back/website/static/{filename}'
                    )
                    print(f"Certificado salvo em: {file_path}")

                    # Adicionar URL de download à lista
                    download_url = url_for('certificate.download_certificate', filename=filename)
                    download_urls.append({'curso': curso.nome, 'url': download_url})

        return render_template('certificate_ready.html', download_urls=download_urls)

    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text
    

@certificate.route('/download_certificate/<filename>')
@login_required
def download_certificate(filename):
    try:
        file_path = os.path.join('static/', filename)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}"
