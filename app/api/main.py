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

@bp.route('/search')
def search():
    a = request.args.get
    print(request.args)
    q = a('q')
    filters = a('filters')
    s_page = a('s_page')
    p_page = a('p_page')
    a = Service.search(q, filters, s_page, p_page)
    return a