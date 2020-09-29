import datetime
from app import db
from app.models import User, PaginatedAPIMixin

class Message(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Unicode()
    datetime = db.Column(db.DateTime, default=datetime.utcnow())
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, body, sender_id, receiver_id):
        sender = User.query.get(sender_id)
        receiver = User.query.get(receiver_id)
        sender.sent_messages.append(self)
        receiver.received_messages.append(self)
        db.session.add(self)

    @staticmethod
    def get_convo(sender_id, receiver_id, page):
        query = Message.query.filter_by(sender_id=sender_id).union\
        (Message.query.filter_by(receiver_id=receiver_id))
        return Message.to_collection_dict(query, page)