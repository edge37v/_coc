from flask import send_from_directory, g, abort, jsonify,request, url_for
from app import db
from app.models import user_subscriptions, Subscription, Lesson, User
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request

@bp.route('/apexlnx/user_subjects')
def user_subjects():
    q = request.args
    id = q['id']
    user = User.query.get(id)
    subscriptions = Subscription.query.join(user_subscriptions, user_subscriptions.c.user_id == user.id)
    years = []
    for a in subscriptions:
        years.append(a)
    return jsonify(Subscription.to_collection_dict(subscriptions))

@bp.route('/apexlnx/subscribe_user/<int:id>', methods=['PUT'])
def subscribe_user():
    pass
