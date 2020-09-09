from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask import g, abort, jsonify, request, url_for
from app import db
from app.models import Subject, Year, Module, Level, User, Lesson, LPlan, user_l_plans
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request, payment_required

@bp.route('/apexlnx/levels', methods=['GET'])
def levels():
    q = Level.to_collection_dict(Level.query)
    return jsonify(q)

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
#@jwt_required
def lessons():
    q = request.get_json()
    query = Lesson.query.filter(Lesson.year.any(name=q['year'])).filter(
        Lesson.subject.any(name=q['subject']))
    if q['module']:
        query = query.filter(Lesson.module.any(name=q['module']))
    if q['level']:
        query = query.filter(Lesson.level.any(name=q['level']))
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    page = request.args.get('page', 1, type=int)
    data = Lesson.to_collection_dict(query, page, per_page, 'api.lessons')
    l = jsonify(data)
    return l

@bp.route('/apexlnx/lessons/<yr>/<sb>', methods=['GET'])
@cross_origin(allow_headers=['Content-Type'])
#@jwt_required
def lessons__yr(yr, sb):
    pass

@bp.route('/apexlnx/lessons/<sb>/<yr>', methods=['GET'])
@jwt_required
def lessons_yr(sb, yr):
    plan = LPlan.query.filter_by(year=yr).first()
    if not g.current_user.subscribed(plan):
        return payment_required('The user needs to pay to access this')
    query = Lesson.query.filter(
                Lesson.subject.any(sid=sb)).filter(
                    Lesson.year.any(sid=yr))
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    page = request.args.get('page', 1, type=int)
    data = Lesson.to_collection_dict(query, page, per_page, 'api.lessons_yr')
    return jsonify(data)

@bp.route('/apexlnx/lessons/<sb>/<yr>/<md>', methods=['GET'])
@jwt_required
def lessons_md(sb, yr, md):
    plan = LPlan.query.filter_by(year=yr).first()
    if not g.current_user.subscribed(plan):
        return payment_required('The user needs to pay to access this')
    query = Lesson.query.filter(
                Lesson.subject.any(sid=sb)).filter(
                    Lesson.year.any(sid=yr)).filter(
                        Lesson.module.any(sid=md))
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    page = request.args.get('page', 1, type=int)
    data = Lesson.to_collection_dict(query, page, per_page, 'api.lessons_md')
    return jsonify(data)

@bp.route('/apexlnx/lessons/<sb>/<yr>/<md>/<lv>', methods=['GET'])
@jwt_required
def lessons_lv(sb, yr, md, lv):
    plan = LPlan.query.filter_by(year=yr).first()
    if not g.current_user.subscribed(plan):
        return payment_required('The user needs to pay to access this')
    query = Lesson.query.filter(
                Lesson.subject.any(sid=sb)).filter(
                    Lesson.year.any(sid=yr)).filter(
                        Lesson.module.any(sid=md)).filter(
                            Lesson.level.any(sid=lv))
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    page = request.args.get('page', 1, type=int)
    data = Lesson.to_collection_dict(query, page, per_page, 'api.lessons_lv')
    return jsonify(data)

@bp.route('/apexlnx/lessons/<int:id>', methods=['GET'])
@jwt_required
def lesson(sb, position):
    shift = request.args.get('shift', 0, type=float)
    lesson = Lesson.query.filter(
                Lesson.subject.any(sid=sb)).filter_by(
                    position=position+shift).first()
    plan = LPlan.query.filter_by(year=lesson.year).first()
    if not g.current_user.subscribed(plan):
        return payment_required('The user needs to pay to access this')
    #Lesson.query.filter_byposition=position
    #shift = request.args.get('shift', 0, type=float)
    g.current_user.lesson_progress = id
    lesson = Lesson.query.get(id)
    data = lesson.to_dict()
    return jsonify(data)

@bp.route('/apexlnx/plans', methods=['GET'])
def plans():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = LPlan.to_collection_dict(LPlan.query, page, per_page, 'api.plans')
    return jsonify(data)