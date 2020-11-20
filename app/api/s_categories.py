from app.api import bp
from app.service_models import SCategory
from flask import request, jsonify
from flask_jwt_extended import jwt_required

@bp.route('/s_categories/archive', methods=['PUT'])
@jwt_required
def archive_s_category():
    ids = request.json.get('ids')
    token = request.headers['Authorization']
    return SCategory.archive(id, token)

@bp.route('/s_categories/unarchive', methods=['PUT'])
@jwt_required
def unarchive_s_category():
    id = request.args.get('id')
    token = request.headers['Authorization']
    return SCategory.unarchive(id, token)

@bp.route('/s_categories', methods=['PUT'])
@jwt_required
def edit_s_category():
    q = request.json.get
    token = request.headers['Authorization']
    id = q('id')
    name = q('name')
    fields = q('fields')
    paid_in = q('paid_in')
    return SCategory.edit(id, token, name, fields, paid_in)

@bp.route('/s_categories', methods=['GET'])
@jwt_required
def search_s_categories():
    query = request.args.get('q')
    return SCategory.search(query)

@bp.route('/s_categories', methods=['POST'])
@jwt_required
def add_s_category():
    q = request.json.get
    token = request.headers['Authorization']
    id = q('id')
    name = q('name')
    json = q('json')
    fields = q('fields')
    paid_in = q('paid_in')
    s = SCategory(name, token, fields, json)
    return jsonify({'s_categories': s.dict()})

@bp.route('/s_categories/add_service', methods=['PUT'])
@jwt_required
def add_service_to_s_category():
    j = request.json.get
    service_id = j('service_id')
    s_categories_id = j('s_categories_id')
    SCategory.add_service(service_id, s_categories_id)

@bp.route('/s_categories/remove_service', methods=['PUT'])
@jwt_required
def remove_service_from_s_category():
    j = request.json.get
    service_id = j('service_id')
    s_categories_id = j('s_categories_id')
    SCategory.remove_service(service_id, s_categories_id)

@bp.route('/s_categories/add_s_class', methods=['PUT'])
@jwt_required
def add_s_class_to_s_category():
    j = request.json.get
    s_class_id = j('s_class_id')
    s_categories_id = j('s_categories_id')
    SCategory.add_s_class(s_class_id, s_categories_id)

@bp.route('/s_categories/remove_s_class', methods=['PUT'])
@jwt_required
def remove_s_class_from_s_category():
    j = request.json.get
    s_class_id = j('s_class_id')
    s_categories_id = j('s_categories_id')
    SCategory.remove_s_class(s_class_id, s_categories_id)

@bp.route('/s_categories/<int:id>', methods=['GET'])
def s_categories(id):
    return jsonify(SCategory.query.get(id).dict())

@bp.route('/s_categories', methods=['DELETE'])
def del_categories():
    q = request.args.get
    token = request.headers['Authorization']
    ids = q('ids')
    SCategory.delete(ids, token)
    return jsonify({})
