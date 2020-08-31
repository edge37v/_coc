from flask import g, abort, jsonify, request, url_for
from app import db
from app.models import User, Plan
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request

@bp.route('/apexlnx/subscribe_user/<int:id>', methods=['PUT'])
def subscribe_user(user_id, plan_id):
    user = User.query.get(id)
    plan = Plan.query.get(id)
    user.subscribe(plan)
    return jsonify(user.to_dict())
