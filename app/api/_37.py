from app.api import bp
from app._37m import Text
from flask import request, jsonify

@bp.route('/search', methods=['GET'])
def _37search():
    q = request.args.get
    rq = q('q')
    page = float(q('page'))
    z = Text.search(rq, page, 21)
    return jsonify(z)

@bp.route('/add/<body>', methods=['POST'])
def post(body):
    Text(body)
    query = Text.query.order_by(Text.time.desc())
    data = Text.to_collection_dict(query, 1, 21)
    z = jsonify(data)
    return z

@bp.route('/texts', methods=['GET'])
def texts():
    q = request.args.get
    page = float(q('page'))
    qq = Text.query.order_by(Text.time.desc())
    z = Text.to_collection_dict(qq, page, 21)
    return jsonify(z)