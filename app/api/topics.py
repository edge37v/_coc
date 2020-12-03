from app.api import bp
from flask import request, jsonify
from app.models import Topic, cdict
from flask_jwt_extended import jwt_required

@bp.route('/topics', methods=['DELETE'])
@jwt_required
def delete_topic():
	id = request.args.get('id')
	Topic.query.get(id).delete()
	return jsonify({'yes': True})

@bp.route('/topics', methods=['GET'])
def get_topic():
	id = request.args.get('id')
	return jsonify(Topic.query.get(id).dict())

@bp.route('/topics', methods=['POST'])
@jwt_required
def add_topic():
	errors = []
	name = request.json.get('name')
	if Topic.query.filter_by(name=name).first():
		errors.append('Topic with that name already exists')
		return jsonify({'errors': errors})
	Topic(name)
	return jsonify({'yes': True})

@bp.route('/topics/search', methods=['GET'])
def search_topics():
	q = request.args.get('q')
	topics = Topic.query.search('"' + q + '"')
	return jsonify([{'id': c.id, 'text': c.name} for c in topics])

@bp.route('/topics/<page>', methods=['GET'])
def get_topics(page):
	return jsonify(cdict(Topic.query, page))