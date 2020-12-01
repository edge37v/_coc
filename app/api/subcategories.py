from app.api import bp
from flask import request, jsonify
from app.models import Subcategory, cdict
from flask_jwt_extended import jwt_required

@bp.route('/subcategories', methods=['DELETE'])
@jwt_required
def delete_subcategory():
	id = request.args.get(id)
	Subcategory.query.get(id).delete()
	return jsonify({'202': True})

@bp.route('/subcategories', methods=['POST'])
@jwt_required
def add_subcategory():
	errors = []
	j = request.json.get
	name = j('name')
	if Subcategory.query.filter_by(name=name).first():
		errors.append('Subcategory with that name already exists')
		return jsonify({'errors': errors})
	id = j('id')
	subcategory = Subcategory(name, id)
	return jsonify({'subcategory': subcategory.dict()})

@bp.route('/subcategories/from_category')
def get_subcategories_from_category():
	a = request.args.get
	id = a('id')
	page = a('page')
	return cdict(Subcategory.query.filter_by(category_id=id), page)

@bp.route('/subcategories/search/<q>', methods=['GET'])
@jwt_required
def search_subcategories(q):
	subcategories = Subcategory.query.filter(Subcategory.ilike(q))
	return jsonify([{'id': s.id, 'text': s.text} for s in subcategories])

@bp.route('/subcategories/<page>', methods=['GET'])
def get_subcategories(page):
	return jsonify(cdict(Subcategory.query, page))

@bp.route('/subcategories', methods=['GET'])
def get_subcategory():
	id = request.args.get('id')
	return jsonify(Subcategory.query.get(id).dict())