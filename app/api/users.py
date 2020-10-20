from flask_jwt_extended import jwt_required, create_access_token
from flask import g, abort, jsonify, request, url_for
from app import db
from app.models import User
from app.api import bp
from app.email import send_user_email
from app.api.auth import token_auth
from app.api.errors import res, bad_request

@bp.route('/users/check', methods=['POST'])
def check(email):
    q = request.get_json()
    email = q['email']
    user = User.query.filter_by(email=email).first()
    if user:
        return res(200, True)
    return res(401, False)

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
    q = request.get_json() or {}
    if 'email' not in q or 'password' not in q:
        return bad_request('must include email and password fields')
    if User.query.filter_by(email=q['email']).first():
        return bad_request('please use a different email')
    user = User()
    user.from_dict(q, new_user=True)
    user.token = create_access_token(identity=q['email'])
    db.session.add(user)
    db.session.commit()
    res = jsonify({'user': user.to_dict()})
    res.status_code = 201
    return res

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