from app.api import bp
from flask import request, jsonify
from app.models import Subtopic, cdict
from flask_jwt_extended import jwt_required

@bp.route('/subtopics', methods=['PUT'])
@jwt_required
def edit_subtopic():
	j = request.json.get
	id = j('id')
	name = j('name')
	Subtopic.edit(id, name)
	return jsonify({'yes': True})

@bp.route('/subtopics', methods=['DELETE'])
@jwt_required
def delete_subtopic():
	id = request.args.get(id)
	Subtopic.query.get(id).delete()
	return jsonify({'yes': True})

@bp.route('/subtopics', methods=['POST'])
@jwt_required
def add_subtopic():
	errors = []
	j = request.json.get
	name = j('name')
	if Subtopic.query.filter_by(name=name).first():
		errors.append('Subtopic with that name already exists')
		return jsonify({'errors': errors})
	id = j('id')
	subtopic = Subtopic(name, id)
	return jsonify({'subtopic': subtopic.dict()})

@bp.route('/subtopics/from_topic')
def get_subtopics_from_topic():
	a = request.args.get
	id = a('id')
	page = a('page')
	return cdict(Subtopic.query.filter_by(topic_id=id), page)

@bp.route('/subtopics/search/<q>', methods=['GET'])
@jwt_required
def search_subtopics(q):
	subtopics = Subtopic.query.filter(Subtopic.ilike(q))
	return jsonify([{'id': s.id, 'text': s.text} for s in subtopics])

@bp.route('/subtopics/<page>', methods=['GET'])
def get_subtopics(page):
	return jsonify(cdict(Subtopic.query, page))

@bp.route('/subtopics', methods=['GET'])
def get_subtopic():
	id = request.args.get('id')
	return jsonify(Subtopic.query.get(id).dict())