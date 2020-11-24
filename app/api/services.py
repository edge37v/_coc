from app.api import bp
from app.service_models import Service
from app.api.fields import add_field
from flask import request, jsonify
from flask_jwt_extended import jwt_required

@bp.route('/services/search', methods=['PUT'])
def search_services():
    j = request.json.get
    q = j('q') or ''
    page = j('page')
    filters = j('filters')
    position = j('position')
    return Service.search(q, page, filters, position)

@bp.route('/services', methods=['POST'])
@jwt_required
def add_service():
    q = request.json.get
    token = request.headers['Authorization']
    name = q('name')
    json = q('json')
    s_class_ids = q('s_class_id')
    fields = q('fields')
    about = q('about')
    price = q('price')
    paid_in = q('paid_in')
    s = Service(json, token, name, s_class_ids, fields, about, price, paid_in)
    if not s:
        return {}, 401
    fields = fields + json
    for f in fields:
        add_field(f['name'])
    return jsonify({'service': s.dict()})

@bp.route('/service/viewed/<int:id>', methods=['PUT'])
def viewed(id):
    json = request.json.get
    if request.headers.get('Origin') != app.config['FRONT_END']:
        return abort(401)
    ip = json('ip')
    service = Service.query.get(id)
    service.json

@bp.route('/services/save', methods=['PUT'])
@jwt_required
def save_service(id):
    token = request.headers['Authorization']
    ids = request.json.get('ids')
    return Service.save(ids, token)

@bp.route('/service/unsave', methods=['PUT'])
@jwt_required
def unsave_service(id):
    token = request.headers['Authorization']
    ids = request.json.get('ids')
    return Service.unsave(ids, token)

@bp.route('/services/archive/<int:id>', methods=['PUT'])
@jwt_required
def archive_service(id):
    token = request.headers['Authorization']
    return Service.archive(id, token)

@bp.route('/services/unarchive/<int:id>', methods=['PUT'])
@jwt_required
def unarchive_service(id):
    token = request.headers['Authorization']
    return Service.unarchive(id, token)

@bp.route('/services', methods=['PUT'])
@jwt_required
def edit_service():
    q = request.json.get
    token = request.headers['Authorization']
    id = q('id')
    name = q('name')
    json = q('json')
    return Service.edit(id, token, name, json)

@bp.route('/services', methods=['GET'])
def services():
    q = request.args.get
    id = q('id')
    page = q('page')
    s = Service.query.filter_by(user_id = id)
    return jsonify(Service.cdict(s, page))

@bp.route('/services/<int:id>', methods=['GET'])
def service(id):
    return jsonify(Service.query.get(id).dict())

@bp.route('/services', methods=['DELETE'])
def del_services():
    token = request.headers['Authorization']
    ids = request.args.get('ids')
    return Service.delete(ids, token)