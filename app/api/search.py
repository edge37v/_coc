from flask import jsonify
from app.api import bp
from app.models import ccdict, Entry, Subtopic, Topic

@bp.route('/search')
def search():
	a = request.query.args
	q = a('q')
	page = a('q')
	queries = [
		Entry.query.search('"' + q + '"'),
		Topic.query.search('"' + q + '"'),
		Subtopic,query.search('"' + q + '"')
	]
	return jsonify(ccdict(queries, page))