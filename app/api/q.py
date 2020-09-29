from flask_jwt_required import jwt_required
from flask import request, jsonify
from q_models import Message
from app import db
from app.api import bp

@bp.route('/q/send', methods=['POST'])
@jwt_required
def send():
    q = request.get_json()
    sender_id = q['sender_id']
    receiver_id = q['receiver_id']
    Message(body, sender_id, receiver_id)

@bp.route('/q/get_convo', methods=['GET'])
@jwt_required
def get_convo():
    page = request
    sender_id = request.args['sender_id']
    receiver_id = request.args['receiver_id']
    data = Message.get_convo(sender_id, receiver_id)
    return jsonify(data)