from app.api import bp
from app.models import Product
from flask import request, jsonify
from flask_jwt_extended import jwt_required

@bp.route('/products', methods=['POST'])
@jwt_required
def add_product():
    print(request.json)
    q = request.json.get
    token = request.authorization
    id = q('id')
    name = q('name')
    json = q('json')
    s = Product(json, id, name)
    return jsonify({'product': 'product'})

@bp.route('/products', methods=['GET'])
def products():
    q = request.args.get
    id = q('id')
    page = q('page')
    s = Product.query.filter_by(user_id = id)
    return jsonify(Product.cdict(s, page, 37))

@bp.route('/products/<int:id>', methods=['GET'])
def product(id):
    return jsonify(Product.query.get(id).dict())

@bp.route('/products', methods=['DELETE'])
def del_product():
    q = request.args.get
    ids = q('ids')
    for id in ids:
        Product.delete(id)
    return jsonify({})
