import re
import boto3
import base64, os, jwt
from time import time
from app import db
from app.models import PaginatedAPIMixin
from datetime import datetime, timedelta

forum_posts = db.Table('forum_posts',
    db.Column('forum_id', db.Integer, db.ForeignKey('forum.id')),
    db.Column('forumpost_id', db.Integer, db.ForeignKey('forumpost.id')))

class Forum(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    posts = db.relationship('Forumpost', secondary=forum_posts, backref='forum', lazy=True)

class Forumpost(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Unicode)