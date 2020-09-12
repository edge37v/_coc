from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response

def wrong_password(message):
    return response(401, message)

def bad_request(message):
    return response(400, message)

def payment_required(message):
    return response(402, message)