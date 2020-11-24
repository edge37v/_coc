from app.api import bp
from app.service_models import SClass
from flask import request, jsonify
from flask_jwt_extended import jwt_required

@bp.route('/s_classes/archive', methods=['PUT'])
@jwt_required
def archive_s_classes():
    ids = request.json.get('ids')
    token = request.headers['Authorization']
    return SClass.archive(ids, token)

@bp.route('/s_classes/unarchive', methods=['PUT'])
@jwt_required
def unarchive_s_class():
    ids = request.json.get('ids')
    token = request.headers['Authorization']
    return SClass.unarchive(ids, token)

@bp.route('/s_classes', methods=['PUT'])
@jwt_required
def edit_s_classes():
    q = request.json.get
    token = request.headers['Authorization']
    id = q('id')
    name = q('name')
    fields = q('fields')
    paid_in = q('paid_in')
    return SClass.edit(id, token, name, fields, paid_in)

@bp.route('/s_classes/qsearch/<q>/<page>', methods=['GET'])
@jwt_required
def search_s_classes_q(q, page):
    token = request.headers['Authorization']
    return SClass.qsearch(q, page, token)

@bp.route('/s_classes/search/<q>', methods=['GET'])
@jwt_required
def search_s_classes(q):
    token = request.headers['Authorization']
    return SClass.search(q, token)

@bp.route('/s_classes/global/search/<q>', methods=['GET'])
@jwt_required
def search_s_classes(q):
    return SClass.global_search(q)

@bp.route('/s_classes', methods=['POST'])
@jwt_required
def add_s_class():
    j = request.json.get
    token = request.headers['Authorization']
    json = j('json')
    name = j('name')
    about = j('about')
    fields = j('fields')
    paid_in = j('paid_in')
    s_class = SClass(json, about, token, name, fields, paid_in)
    return jsonify(s_class.dict())

@bp.route('/s_classes/add_service', methods=['PUT'])
@jwt_required
def add_service_to_s_class():
    j = request.json.get
    service_id = j('service_id')
    class_id = j('class_id')
    SClass.add(service_id, class_id)

@bp.route('/s_classes/remove_service', methods=['PUT'])
@jwt_required
def remove_service_from_class():
    j = request.json.get
    service_id = j('service_id')
    class_id = j('class_id')
    SClass.remove(service_id, class_id)

@bp.route('/s_classes/get_s/<int:id>', methods=['GET'])
def get_s_class_fields(id):
    if float(id) < 1:
        return {}
    s_class = SClass.query.get(id)
    if s_class:
        return jsonify({'name': s_class.name, 'fields': s_class.fields})
    return {}

@bp.route('/s_classes/<int:id>', methods=['GET'])
def s_class(id):
    return jsonify(SClass.query.get(id).dict())

@bp.route('/s_classes/delete', methods=['PUT'])
@jwt_required
def del_s_classes():
    token = request.headers['Authorization']
    ids = request.json.get('ids')
    return SClass.delete(ids, token)