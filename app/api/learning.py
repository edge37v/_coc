from flask import g, abort, jsonify, request, url_for
from app import db
from app.models import User, Lesson
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request

@bp.route('/apexlnx/lessons/<sb>/', methods=['GET'])
def lessons_sb(subject):
    query = Lesson.query.filter(Lesson.subject.any(sid=subject))
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    page = request.args.get('page', 1, type=int)
    data = Lesson.to_collection_dict(query, page, per_page, api.lessons_sb)
    return jsonify(data)

@bp.route('/apexlnx/lessons/<sb>/<yr>', methods=['GET'])
def lessons_sb_yr(sb, yr):
    query = Lesson.query.filter(
                Lesson.subject.any(sid=sb)).filter(
                    Lesson.year.any(sid=yr))
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    page = request.args.get('page', 1, type=int)
    data = Lesson.to_collection_dict(query, page, per_page, api.lessons_sb_yr)
    return jsonify(data)

@bp.route('/apexlnx/lessons/<sb>/<yr>/<md>', methods=['GET'])
def lessons_sb_yr_md(sb, yr, md):
    query = Lesson.query.filter(
                Lesson.subject.any(sid=sb)).filter(
                    Lesson.year.any(sid=yr)).filter(
                        Lesson.module.any(sid=md))
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    page = request.args.get('page', 1, type=int)
    data = Lesson.to_collection_dict(query, page, per_page, api.lessons_sb_yr_md)
    return jsonify(data)

@bp.route('/apexlnx/lessons/<sb>/<yr>/<md>/<lv>', methods=['GET'])
def lessons_sb_yr_md_lv(sb, yr, md, lv):
    query = Lesson.query.filter(
                Lesson.subject.any(sid=sb)).filter(
                    Lesson.year.any(sid=yr)).filter(
                        Lesson.module.any(sid=md)).filter(
                            Lesson.level.any(sid=lv))
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    page = request.args.get('page', 1, type=int)
    data = Lesson.to_collection_dict(query, page, per_page, api.lessons_sb_yr_md_lv)
    return jsonify(data)

@bp.route('/apexlnx/lessons/<int:id>', methods=['GET'])
def lesson(sb, position):
    shift = request.args.get('shift', 0, type=float)
    lesson = Lesson.query.filter(
                Lesson.subject.any(sid=sb)).filter_by(
                    position=position+shift).first()
    Lesson.query.filter_byposition=position
    shift = request.args.get('shift', 0, type=float)
    g.current_user.lesson_progress = id
    lesson = Lesson.query.get(id)
    data = Lesson.to_dict()
    return jsonify(data)

@bp.route('/apexlnx/plans', methods=['GET'])
def get_plans():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Plan.to_collection_dict(Plan.query.all(), page, per_page, api.get_plans)
    return jsonify(data)