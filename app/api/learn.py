from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask import send_from_directory, g, abort, jsonify, request, url_for
from app import db
from app.models import Subject, Year, Module, User, Lesson
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request, payment_required

@bp.route('/learn/ls', methods=['PUT'])
def ls():
    q = request.args.get
    User.query.get(q('id')).ls = q('ls')
    db.session.commit()
    return jsonify({'code': 201})

@bp.route('/learn/ly', methods=['PUT'])
def ly():
    q = request.args.get
    User.query.get(q('id')).ly = q('ly')
    db.session.commit()
    return jsonify({'code': 201})

@bp.route('/learn/ls', methods=['GET'])
def get_ls():
    return jsonify({'ls': User.query.get(request.args['id']).ls})

@bp.route('/learn/ly', methods=['GET'])
def get_ly():
    return jsonify({'ly': User.query.get(request.args['id']).ly})


@bp.route('/learn/search', methods=['GET'])
def search():
    r = request.args.get
    per_page = r('per_page')
    page = r('page')
    q = r('q')
    return jsonify(Lesson.search(q, page, per_page))

@bp.route('/learn/years', methods=['GET'])
def years():
    years = [year.to_dict() for year in Year.query]
    return jsonify({'years': years})

@bp.route('/subjects', methods=['GET'])
def subjects():
    #query = Subject.query
    #data = Subject.to_collection_dict(Subject.query, 1, 10, 'api.subjects')
    subjects = [subject.to_dict() for subject in Subject.query]
    return jsonify({'subjects': subjects})

@bp.route('/learn', methods=['GET'])
#jwt_required
def lessons():
    q = request.args.get
    query = Lesson.query
    if q('subject'):
        query = query.filter(Lesson.subject.any(name=str(q('subject'))))
    if q('year'):
        query = query.filter(Lesson.year.any(name=str(q('year'))))
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    page = request.args.get('page', 1, type=int)
    data = Lesson.to_collection_dict(query, page, per_page, 'api.lessons')
    l = jsonify(data)
    return l