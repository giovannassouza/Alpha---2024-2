from flask import Blueprint, jsonify
from flask_wtf.csrf import generate_csrf

csrf_ = Blueprint('csrf', __name__)

@csrf_.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    csrf_token = generate_csrf()
    response = jsonify({'csrf_token': csrf_token})
    
    # Adiciona os cabeçalhos CORS necessários
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    
    return response
