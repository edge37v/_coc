from flask_jwt_extended import jwt_required, create_access_token
from flask_cors import cross_origin
from werkzeug.datastructures import Headers
from flask import make_response, request, jsonify, g
from app import db
from app.models import User
from app.api import bp
from app.api.errors import wrong_password, bad_request, payment_required, res

@bp.route('/tokens', methods=['POST'])
def get_token():
    q = request.get_json()
    headers = Headers()
    errors = []
    headers.add('Access-Control-Allow-Origin', request.headers.get('Origin'))
    email = q['email']
    password = q['password']
    user = User.query.filter_by(email=email).first()
    if not user:
        errors.append('User does not exist')
        return jsonify({'errors': errors})
    if not user.check_password(password):
        errors.append('Wrong Password')
        return jsonify({'errors': errors})
    #if not user.confirmed:
     #   errors.append('User is not subscribed')
      #  return jsonify({'errors': errors})
    user.token = create_access_token(identity=email)
    g.current_user = user
    db.session.add(user)
    db.session.commit()
    res_body = {'user': user.dict()}
    res = make_response(res_body, headers)
    return res

@bp.route('/tokens', methods=['DELETE'])
def revoke_token():
    id = request.args['id']
    user = User.query.get(id)
    user.revoke_token()
    db.session.commit()
    return '', 204