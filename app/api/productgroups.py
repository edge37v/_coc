from app.api import bp
from flask import request
from app.models import Productgroup
from flask_jwt_extended import jwt_required

@bp.route('/groups', methods=['POST'])
@jwt_required
def add_productgroup():
    q = request.args.get
    id = q('id')
    name = q('name')
    Productgroup(id, name)

@bp.route('/groups', methods=['PUT'])
@jwt_required
def edit_prodouctgroup():
    q = request.get_json()
    user_id = q['user_id']
    group_id = q['group_id']
    Productgroup.edit(user_id, group_id)


