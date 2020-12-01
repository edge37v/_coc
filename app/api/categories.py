from app.api import bp
from flask import request, jsonify
from app.models import Category, cdict
from flask_jwt_extended import jwt_required

@bp.route('/categories', methods=['DELETE'])
@jwt_required
def delete_category():
	id = request.args.get('id')
	Category.query.get(id).delete()
	return jsonify({'yes': True})

@bp.route('/categories', methods=['GET'])
def get_category():
	id = request.args.get('id')
	return jsonify(Category.query.get(id).dict())

@bp.route('/categories', methods=['POST'])
@jwt_required
def add_category():
	errors = []
	name = request.json.get('name')
	if Category.query.filter_by(name=name).first():
		errors.append('Category with that name already exists')
		return jsonify({'errors': errors})
	Category(name)
	return jsonify({'yes': True})

@bp.route('/categories/search', methods=['GET'])
def search_categories():
	q = request.args.get('q')
	categories = Category.query.filter(Category.name.ilike(q))
	return jsonify([{'id': c.id, 'text': c.name} for c in categories])

@bp.route('/categories/<page>', methods=['GET'])
def get_categories(page):
	return jsonify(cdict(Category.query, page))