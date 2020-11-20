from app.api import bp
from app.models import Field
from app.service_models import Service
from flask import request, jsonify
from flask_jwt_extended import jwt_required

@bp.route('/fields')
def fields():
    q = request.args.get('q')
    print(q)
    return jsonify([f.dict() for f in Field.search(q)])