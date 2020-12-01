from flask_jwt_extended import jwt_required, create_access_token
from flask_cors import cross_origin
from werkzeug.datastructures import Headers
from flask import current_app, request, jsonify
from app.api import bp

@bp.route('/tokens', methods=['POST'])
def get_token():
    q = request.get_json()
    headers = Headers()
    errors = []
    headers.add('Access-Control-Allow-Origin', request.headers.get('Origin'))
    password = q['password']
    system_password = current_app.config['SYSTEM_PASSWORD']
    if password != system_password:
        errors.append({'id': 1, 'kind': 'error', 'title': 'Wrong Password'})
        return jsonify({'errors': errors})
    token = create_access_token(identity=37)
    return {'token': token}

@bp.route('/tokens', methods=['DELETE'])
@jwt_required
def revoke_token():
    token = request.headers.get('Authorization')
    return jsonify({'yes': True})