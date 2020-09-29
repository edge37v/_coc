import re
import boto3
import base64, os, jwt
from time import time
from app import db
from app.models import PaginatedAPIMixin
from datetime import datetime, timedelta

forum_posts = db.Table('forum_posts',
    db.Column('forum_id', db.Integer, db.ForeignKey('forum.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')))

class Forum(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    posts = db.relationship('ForumPost', secondary=forum_posts, backref='forum', lazy=True)

class ForumPost(PaginatedAPIMixin, db.Model):