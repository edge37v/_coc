from flask_jwt_extended import jwt_required, create_access_token
from flask_cors import cross_origin
from werkzeug.datastructures import Headers
from flask import make_response, request, jsonify, g
from app import db
from app.models import User
from app.api import bp
from app.api.errors import wrong_password, bad_request, payment_required, response

@bp.route('/tokens', methods=['POST'])
def get_token():
    q = request.get_json()
    d = Headers()
    d.add_header('Access-Control-Allow-Origin', request.headers.get('Origin'))
    user = User.query.filter_by(email=q['email']).first()
    if not user:
        return bad_request('User does not exist')
    if not user.check_password(q['password']):
        return wrong_password('Wrong Password')
    if not user.confirmed:
        return payment_required('User is not subscribed')
    token = create_access_token(identity=q['email'])
    u = user.to_dict()
    u['token'] = token
    r = jsonify(u)
    res = make_response(u, d)
    return res

@bp.route('/tokens', methods=['DELETE'])
def revoke_token():
    user.revoke_token()
    db.session.commit()
    return '', 204