from flask import Blueprint, Flask, render_template
from flask_login import login_required, current_user
from .certificate_api import gerar_certificado_pdf
from .models import *
from website.models import *

certificate = Blueprint('certificate', __name__)

@certificate.route('/class/certificate', methods=['GET'])
# @login_required
def get_certificate():
    try:
        cursosFeitos = db.session.execute(db.select(CursosEmProgresso).filter_by(user_id = current_user.get_id())).scalar_one()
        user_data = db.session.execute(db.select(User).filter_by(id=current_user.get_id()))
        gerar_certificado_pdf(user_data.full_name, cursosFeitos.name, cursosFeitos.horas_estimado)
        return "<p>Certificado Gerado!</p>"

    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text