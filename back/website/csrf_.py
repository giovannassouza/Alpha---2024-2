from flask import Blueprint, jsonify
from flask_wtf.csrf import generate_csrf

csrf_ = Blueprint('csrf', __name__)

@csrf_.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    csrf_token = generate_csrf()
    return jsonify({'csrf_token': csrf_token})