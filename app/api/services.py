from app.api import bp
from app.models import Service
from flask import request, jsonify
from flask_jwt_extended import jwt_required

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
def save_service():
    id = request.args.get('id')
    token = request.headers['Authorization']
    return Service.save(id, token)

@bp.route('/services/unsave', methods=['PUT'])
@jwt_required
def unsave_service():
    id = request.args.get('id')
    token = request.headers['Authorization']
    return Service.unsave(id, token)

@bp.route('/services/archive', methods=['PUT'])
@jwt_required
def archive_service():
    ids = request.json.get('ids')
    token = request.headers['Authorization']
    return Service.archive(id, token)

@bp.route('/services/unarchive', methods=['PUT'])
@jwt_required
def unarchive_service():
    id = request.args.get('id')
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

@bp.route('/services', methods=['POST'])
@jwt_required
def add_service():
    q = request.json.get
    token = request.headers['Authorization']
    id = q('id')
    name = q('name')
    json = q('json')
    about = q('about')
    prices = q('prices')
    currency = q('currency')
    s = Service(json, id, name, about, prices, currency)
    return jsonify({'service': s.dict()})

@bp.route('/services', methods=['GET'])
def services():
    q = request.args.get
    id = q('id')
    page = q('page')
    s = Service.query.filter_by(user_id = id)
    return jsonify(Service.cdict(s, page, 37))

@bp.route('/services/<int:id>', methods=['GET'])
def service(id):
    return jsonify(Service.query.get(id).dict())

@bp.route('/services', methods=['DELETE'])
def del_services():
    q = request.args.get
    token = request.headers['Authorization']
    ids = q('ids')
    for id in ids:
        Service.delete(id, token)
    return jsonify({})
