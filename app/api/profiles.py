from flask import request, jsonify
from app.models import Profile
from app.api import bp

@bp.route('/add_profile', methods=['POST'])
def add_profile():
    q = request.get_json()
    id = q['id'] or None
    email = q['email'] or None
    name = q['name']
    user = User.query.get(id)
    profile = Profile(user, name)
    return {'code': 201}
    

@bp.route('/add_service', methods=['PUT'])
def add_service():
    q = request.get_json()
    user_id = q['user_id']
    profile_id = q['profile_id']
