from flask import jsonify, g
from app import db
from app.api import bp
from app.api.errors import error_response
from app.api.auth import basic_auth, token_auth

@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    #if not g.current_user.confirmed:
    #    return error_response(401, 'User not confirmed')
    token = g.current_user.get_token()
    db.session.commit()
    response = {'user': g.current_user.to_dict()}
    response.token = token
    return jsonify(response)

@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204