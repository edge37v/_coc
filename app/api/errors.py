from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def res(status_code, message=None):
    payload = {'code': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    return payload

def wrong_password(message):
    return res(401, message)

def bad_request(message):
    return res(400, message)

def payment_required(message):
    return res(402, message)