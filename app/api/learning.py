from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask import g, abort, jsonify, request, url_for
from app import db
from app.models import Subject, Year, Module, User, Lesson
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request, payment_required

@bp.route('/apexlnx/user_years', methods=['GET'])
def user_years():
    id=request.args.get('id')
    u=User.query.get(id)
    y = Year.to_collection_dict(u.years)
    return y

@bp.route('/apexlnx/user_modules', methods=['GET'])
def user_modules():
    id=request.args.get('id')
    m = Module.to_collection_dict(m.modules)
    return jsonify(m)

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

@bp.route('/apexlnx/lessons/<yr>/<sb>', methods=['GET'])
@cross_origin(allow_headers=['Content-Type'])
def lessons__yr(yr, sb):
    pass

@bp.route('/apexlnx/lessons/<int:id>', methods=['GET'])
@jwt_required
def lesson_page(sb, position):
    shift = request.args.get('shift', 0, type=float)
    lesson = Lesson.query.filter(
                Lesson.subject.any(sid=sb)).filter_by(
                    position=position+shift).first()
    #Lesson.query.filter_byposition=position
    #shift = request.args.get('shift', 0, type=float)
    g.current_user.lesson_progress = id
    lesson = Lesson.query.get(id)
    data = lesson.to_dict()
    return jsonify(data)