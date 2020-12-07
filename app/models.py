import re
import math
import boto3
import base64, os, jwt
from time import time
from app import db
from flask import jsonify
from geopy import distance
from datetime import datetime, timedelta
from flask_sqlalchemy import BaseQuery
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import make_searchable
from flask import jsonify, current_app, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

class Query(BaseQuery, SearchQueryMixin):
    pass

#combines items in a query-list as a list
def ccdict(queries, page=1, per_page=37):
    data = {}
    dlist = []
    for query in queries:
        dlist = dlist + [item.dict() for item in query]
    start = int(page) * int(per_page)
    end = per_page
    print(start, end)
    data['data'] = dlist[start:end]
    data['total_pages'] = math.ceil(len(dlist)*37)
    data['total_items'] = len(dlist)
    return data

def cdict(query, page=1, per_page=37, endpoint='', **kwargs):
        page = float(page)
        resources = query.paginate(page, per_page, False)
        data = {
            'data': [item.dict() for item in resources.items]
        }
        data['meta'] = {
            'page': page,
            'total_pages': resources.pages,
            'total_items': resources.total
        }
        return data

class Entry(db.Model):
    query_class = Query
    search_vector = db.Column(TSVectorType(
        'name', 'body', weights={'name': 'A', 'body': 'B'}))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True)
    body = db.Column(db.Unicode)
    verses = db.Column(db.JSON)
    rank = db.Column(db.Integer)
    type = db.Column(db.Unicode)
    type_plural = db.Column(db.Unicode)
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopic.id'))

    @staticmethod
    def edit(id, verses=None, name=None, body=None):
        entry = Entry.query.get(id)
        entry.verses = verses or entry.verses
        entry.name = name or entry.name
        entry.body = body or entry.body
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'body': self.body,
            'verses': self.verses,
            'rank': self.rank,
            'type': self.type,
            'subtopic_id': self.subtopic_id,
            'type_plural': self.type_plural
        }
        return data

    def __init__(self, verses, name, body, id):
        subtopic = Subtopic.query.get(id)
        self.subtopic = subtopic
        self.verses = verses
        self.name = name
        self.body = body,
        self.type = 'entry'
        self.type_plural = 'entries'
        db.session.add(self)
        db.session.commit()

class Subtopic(db.Model):
    query_class = Query
    search_vector = db.Column(TSVectorType('name'))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True)
    rank = db.Column(db.Integer)
    type = db.Column(db.Unicode)
    type_plural = db.Column(db.Unicode)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    entries = db.relationship('Entry', backref='subtopic', lazy='dynamic')

    @staticmethod
    def edit(id, name):
        Subtopic.query.get(id).name = name
        db.session.commit()

    def delete(self):
        for entry in self.entries:
            db.session.delete(entry)
        db.session.delete(self)
        db.session.commit()

    def __init__(self, name, id):
        topic = Topic.query.get(id)
        self.name = name
        self.topic = topic
        self.type = 'subtopic'
        self.type_plural = 'subtopics'
        db.session.add(self)
        db.session.commit()  

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'rank': self.rank,
            'type': self.type,
            'type_plural': self.type_plural
        }
        return data

class Topic(db.Model):
    query_class = Query
    search_vector = db.Column(TSVectorType('name'))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True)
    rank = db.Column(db.Integer)
    type = db.Column(db.Unicode)
    type_plural = db.Column(db.Unicode)
    subtopics = db.relationship('Subtopic', backref='topic', lazy='dynamic')

    @staticmethod
    def edit(id, name):
        Topic.query.get(id).name = name
        db.session.commit()

    def delete(self):
        for subtopic in self.subtopics:
            subtopic.delete()
        db.session.delete(self)
        db.session.commit()

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'rank': self.rank,
            'type': self.type,
            'type_plural': self.type_plural
        }
        return data

    def __init__(self, name):
        self.name = name
        self.type = 'topic'
        self.type_plural = 'topics'
        db.session.add(self)
        db.session.commit()    