from app.api import bp
from app.models import Service
from flask import request, jsonify
from flask_jwt_extended import jwt_required

@bp.route('/services', methods=['POST'])
@jwt_required
def add_service():
    print(request.json)
    q = request.json.get
    token = request.authorization
    id = q('id')
    name = q('name')
    json = q('json')
    s = Service(json, id, name)
    return jsonify({'service': 'service'})

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
def del_service():
    q = request.args.get
    ids = q('ids')
    for id in ids:
        Service.delete(id)
    return jsonify({})
