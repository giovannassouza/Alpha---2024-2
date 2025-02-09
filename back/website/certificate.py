import os
from flask import Blueprint, Flask, jsonify, render_template, send_file, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from website.json_responses import *
from .certificate_api import gerar_certificado_pdf
from .models import *
from website.models import *

certificate = Blueprint('certificate', __name__)

@certificate.route('/class/certificate', methods=['POST'])
@login_required
def get_certificate():
    """
    Search for finished classes and make certificates.
    ---
    tags:
      - Certificates
    parameters:
      - name: current_user
        in: formData
        type: User
        required: true
        description: Logged user to search for classes.
    responses:
      200:
        description: Successfully generated certificate.
        schema:
          type: object
          properties:
            download_url:
              type: dict
              description: Dictionary with certificates URLs to download.
    400:
        description: Could not generate certificate.
    404:
        description: Could not find finished classes.
    500:
        description: Internal server error.
    """
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
        
        if len(download_urls) ==0:
            return error_response(description="Could not find finished classes", response=404)
        else:
            return successful_response(description="Succesfully accessed the certificates url.", data={"download_url": download_urls})

    except Exception as e:
        # e holds description of the error
        return error_response(description="Couldn't generate certificate.", error_details={"exception": str(e)})
    

@certificate.route('/download_certificate/<filename>')
@login_required
def download_certificate(filename):
    """
    Endpoint to download a generated certificate.
    ---
    tags:
      - Certificates
    parameters:
      - name: filename
        in: path
        type: string
        required: true
        description: The filename of the certificate to download.
    responses:
      200:
        description: Certificate file.
        schema:
          type: file
      404:
        description: Certificate not found.
    """
    try:
        file_path = os.path.join('static/', filename)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}"
