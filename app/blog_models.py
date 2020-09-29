import random, re, boto3, base64, os, jwt
from time import time
from app import db
from app.models import PaginatedAPIMixin
from datetime import datetime, timedelta

blog_posts = db.Table('blog_posts',
    db.Column('blog_id', db.Integer, db.ForeignKey('blog.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Unicode)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __init__(self, body, post):
        self.body = body
        self.post = post

class Blog(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    forum = db.relationship('Forum', backref='blog', lazy=True)
    posts = db.relationship('BlogPost', secondary=blog_posts, backref='blog', lazy=True)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data

class BlogPost(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    comments = db.relationship(Comment, backref='post', lazy=True)
    body = db.Column(db.Unicode)

    def __init__(self, body):
        db.session.add(self)
        self.body = body

    def add_comment(self, body):
        db.session.add(Comment(body, self))