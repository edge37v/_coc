from app.api import bp
from app.models import Place
from flask import request, jsonify

@bp.route('/places', methods=['GET'])
def places():
    r = request.args.get
    q = r('q')
    return jsonify({'places': [place.dict() for place in Place.search(q)]})