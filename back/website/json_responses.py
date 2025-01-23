from flask import jsonify, Response

def successful_response(description: str = 'Success. ', response: int = 200) -> Response:
    return jsonify({
        'response': response,
        'description': description
    })

def error_response(description: str = 'Error. ', response: int = 400) -> Response:
    return jsonify({
        'response': response,
        'description': description
    })