from app import db
from app.models import User

class Forum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    posts = db.relationship('Post', secondary='forum_posts', backref=db.backref('forum', lazy=True), lazy=True)

    def __init__(self, name):
        self.name = name
        db.session.add(self)

    def to_dict(self):
        data = {
            'name': self.name
        }
        return data

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Unicode(140))
    replies = db.relationship('Reply', backref='post', lazy=True)

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Unicode(140))