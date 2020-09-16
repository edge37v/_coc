from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask import send_from_directory, g, abort, jsonify, request, url_for
from app import db
from app.models import Subject, Year, Module, User, Lesson
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request, payment_required

@bp.route('/apexlnx/modules', methods=['GET'])
def modules():
    q = Module.to_collection_dict(Module.query)
    return jsonify(q)

@bp.route('/apexlnx/years', methods=['GET'])
def years():
    q = Year.to_collection_dict(Year.query)
    return jsonify(q)

@bp.route('/apexlnx/subjects', methods=['GET'])
def subjects():
    q = Subject.to_collection_dict(Subject.query)
    return jsonify(q)

@bp.route('/apexlnx/lessons', methods=['POST'])
def lessons():
    q = request.get_json()
    query = Lesson.query.filter(Lesson.year.any(name=str(q['year']))).filter(
        Lesson.subject.any(name=str(q['subject'])))
    if q['module']:
        query = query.filter(Lesson.module.any(name=str(q['module'])))
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    page = request.args.get('page', 1, type=int)
    data = Lesson.to_collection_dict(query, page, per_page, 'api.lessons')
    l = jsonify(data)
    return l