from flask import request, jsonify
from app.api import bp
from app.models import ccdict, Entry, Subtopic, Topic

@bp.route('/search')
def search():
	a = request.args.get
	q = a('q')
	page = a('page')
	queries = [
		Entry.query.search('"' + q + '"'),
		Topic.query.search('"' + q + '"'),
		Subtopic.query.search('"' + q + '"')
	]
	return jsonify(ccdict(queries, page))