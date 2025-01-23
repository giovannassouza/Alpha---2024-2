from flask import Blueprint
from .models import *
from flask_wtf.csrf import CSRFError
from .json_responses import successful_response, error_response  # Import your standardized response functions

wtf_error = Blueprint('wtf_error', __name__)

@wtf_error.errorhandler(CSRFError)
def handle_csrf_error(e):
    return error_response(
        response=403,
        description='CSRF token missing or invalid.',
        error_type='csrf_error',
        error_details=str(e)
    )
