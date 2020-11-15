from app.api import bp
from app.models import Location
from flask import request, jsonify

@bp.route('/locations', methods=['GET'])
def locations():
    r = request.args.get
    q = r('q')
    return jsonify({'locations': [location.dict() for location in Location.search(q)]})