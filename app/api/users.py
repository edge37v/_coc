from flask_jwt_extended import jwt_required
from flask import g, abort, jsonify, request, url_for
from app import db
from app.models import User
from app.api import bp
from app.email import send_user_email
from app.api.auth import token_auth
from app.api.errors import response, bad_request

@bp.route('/users/check', methods=['POST'])
def check(email):
    q = request.get_json()
    email = q['email']
    user = User.query.filter_by(email=email).first()
    if user:
        return response(200, True)
    return response(401, False)

@bp.route('/users/<int:id>', methods=['GET'])
@jwt_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())

@bp.route('/users', methods=['GET'])
@jwt_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'email' not in data or 'password' not in data:
        return bad_request('must include email and password fields')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    #send_user_email(user)
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@bp.route('/users/<int:id>', methods=['PUT'])
@jwt_required
def update_user(id):
    if g.current_user.id != id:
        abort(403)
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())