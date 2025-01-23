from flask import jsonify, Response
from datetime import datetime
from typing import Any, Optional, Dict

def successful_response(description: str, response: int = 200, data: Optional[Any] = None, meta: Optional[Dict] = None) -> Response:
    """
    Generate a standardized response for successful operations.

    Args:
        description (str): A human-readable message describing the success.
        response (int, optional): The HTTP status code for the response. Defaults to 200.
        data (Any, optional): The payload to return to the front-end. 
            This can include any JSON-serializable object, such as query results or user data. Defaults to None.
        meta (Dict, optional): Additional metadata about the response, such as pagination details. Defaults to None.

    Returns:
        Response: A Flask Response object in JSON format, containing:
            - `response` (int): The HTTP status code.
            - `description` (str): A message describing the success.
            - `data` (Any): The payload of the response (if provided).
            - `error` (None): Set to `None` since this is a successful response.
            - `meta` (Dict): Metadata about the response (if provided).
            - `timestamp` (str): The UTC timestamp of the response in ISO 8601 format.
    """
    return jsonify({
        'response': response,
        'description': description,
        'data': data,
        'error': None,
        'meta': meta,
        'timestamp': datetime.utcnow().isoformat() + "Z"
    })


def error_response(description: str, response: int = 400, error_type: Optional[str] = None, error_details: Optional[Dict] = None) -> Response:
    """
    Generate a standardized response for errors or failures.

    Args:
        description (str): A human-readable message describing the error.
        response (int, optional): The HTTP status code for the response. Defaults to 400.
        error_type (str, optional): A short identifier or category of the error 
            (e.g., "validation_error", "authentication_error"). Defaults to None.
        error_details (Dict, optional): Additional information about the error, such as field-specific validation issues. Defaults to None.

    Returns:
        Response: A Flask Response object in JSON format, containing:
            - `response` (int): The HTTP status code.
            - `description` (str): A message describing the error.
            - `data` (None): Set to `None` since this is an error response.
            - `error` (Dict): A dictionary containing:
                - `type` (str): The error type (if provided).
                - `details` (Dict): Detailed information about the error (if provided).
            - `meta` (None): Set to `None` since additional metadata is not relevant for errors.
            - `timestamp` (str): The UTC timestamp of the response in ISO 8601 format.
    """
    return jsonify({
        'response': response,
        'description': description,
        'data': None,
        'error': {
            'type': error_type,
            'details': error_details
        } if error_type or error_details else None,
        'meta': None,
        'timestamp': datetime.utcnow().isoformat() + "Z"
    })
