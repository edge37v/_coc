from flask_jwt_extended import jwt_required, create_access_token
from flask import g, abort, jsonify, request, url_for
from app import db
from app.models import User, cdict
from app.api import bp
from app.email import send_user_email
from app.api.auth import token_auth
from app.api.errors import res, bad_request

@bp.route('/user/s_classes', methods=['GET'])
@jwt_required
def user_classes(id):
    token = request.headers['Authorization']
    user = User.query.filter_by(token=token).first()
    page = request.args.get('page')
    return jsonify(cdict(user.s_classes, page, 37))

@bp.route('/user/s_categories/<int:id>', methods=['GET'])
def user_s_categories(id):
    q = request.args.get
    page = q('page')
    user = User.query.get(id)
    return jsonify(cdict(user.s_classes, page, 37))


@bp.route('/users/search')
def user_search():
    print(request.args)
    a = request.args.get
    q = a('q')
    id = q('id')
    location = a('location')
    s_page = a('s_page')
    p_page = a('p_page')
    return User.search(location, id, q, s_page, p_page, 37)

@bp.route('/users/<int:id>', methods=['GET'])
def user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.qdict())

@bp.route('/users', methods=['GET'])
@jwt_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    user = User.to_cdict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)

@bp.route('/users', methods=['POST'])
def create_user():
    q = request.get_json()
    errors = []
    email = q['email']
    password = q['password']
    if email is None:
        errors.append('Email required')
        return jsonify({'errors': errors})
    if password is None:
        errors.append('Password required')
        return jsonify({'errors': errors})
    if User.query.filter_by(email=email).first():
        errors.append('Email taken')
        return jsonify({'errors': errors})
    user = User(email, password)
    user.token = create_access_token(identity=email)
    res = jsonify({'user': user.dict()})
    res.status_code = 201
    return res

@bp.route('/users/<int:id>', methods=['PUT'])
@jwt_required
def update_user(id):
    errors = []
    print(request.get_json())
    token = request.headers['Authorization']
    user = User.query.get_or_404(id)
    data = request.get_json()
    if user != User.query.filter_by(token = token).first():
        return {}, 401
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        errors.append('Email taken')
        return {'errors': errors}
    user.from_dict(data)
    db.session.commit()
    return {'user': user.dict()}