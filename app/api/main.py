from flask import g, abort, jsonify, request, url_for
from app import db
from app.models import User
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request

@bp.route('/user_search/<query>')
@token_auth.login_required
def user_search(query):
    query = User.query.search(query).all()
    data = User.to_collection_dict(query, 'api.search')
    return jsonify(data)
