from app.api import bp
from flask import request, jsonify
from app.models import Entry, cdict
from flask_jwt_extended import jwt_required

@bp.route('/entries', methods=['PUT'])
@jwt_required
def edit_entry():
	j = request.json.get
	id = j('id')
	body = j('body')
	verses = j('verses')
	name = j('name')
	Entry.edit(id, verses, name, body)
	return jsonify({'yes': True})

@bp.route('/entries', methods=['DELETE'])
@jwt_required
def delete_entry():
	id = request.args.get('id')
	Entry.query.get(id).delete()
	return jsonify({'yes': True})

@bp.route('/entries/from_subtopic', methods=['GET'])
def get_entries_from_subtopic():
	a = request.args.get
	id = a('id')
	page = a('page')
	return jsonify(cdict(Entry.query.filter_by(subtopic_id=id), page))

@bp.route('/entries', methods=['POST'])
@jwt_required
def add_entry():
	errors = []
	j = request.json.get
	id = j('id')
	verses = j('verses')
	name = j('name')
	if Entry.query.filter_by(name=name).first():
		errors.append('Entry with that name already exists')
		return jsonify({'errors': errors})
	body = j('body')
	entry = Entry(verses, name, body, id)
	return jsonify(entry.dict())

@bp.route('/entries', methods=['GET'])
def get_entry():
	id = request.args.get('id')
	return jsonify(Entry.query.get(id).dict())