from flask import send_from_directory, g, abort, jsonify, request, url_for
from app import db
from app.models import Lesson, User
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request

@bp.route('/apexlnx/subscribe_user/<int:id>', methods=['PUT'])
def subscribe_user():
    pass