from app.api import bp
from flask import request
from flask_jwt_extended import jwt_required

@bp.route('/products', methods=['POST'])
@jwt_required
def add_product():
    q = request.get_json()
    id = q['id']
    name = q['name']
    description = q['description']
    user = User.query.get(id)
    s = Product(user, name)
    return jsonify(s.dict())

@bp.route('/products', methods=['GET'])
def products():
    q = request.args.get
    id = q('id')
    page = q('page')
    s = Product.query.filter_by(user_id = id)
    return jsonify(Product.cdict(s, page, 37))

@bp.route('/products', methods=['GET'])
def product():
    q = request.args.get
    id = q('id')
    return jsonify(Product.query.get(id).dict())

@bp.route('/products', methods=['DELETE'])
@jwt_required
def del_product():
    q = request.args.get
    ids = q('ids')
    for id in ids:
        Product.delete(id)
    return jsonify({})
