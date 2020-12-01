import re
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

db.configure_mappers()

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
        if query.count() < 1:
            data['data'] = []
        if endpoint != '':
            data['_links'] = {
                'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page, 
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        return data

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True)
    body = db.Column(db.Unicode)
    verses = db.Column(db.JSON)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'))

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'body': self.body,
            'verses': self.verses,
            #'subcategory': self.subcategory.dict(),
            #'category': self.subcategory.dict()['category']
        }
        return data

    def __init__(self, verses, name, body, id):
        subcategory = Subcategory.query.get(id)
        self.subcategory = subcategory
        self.verses = verses
        self.name = name
        self.body = body
        db.session.add(self)
        db.session.commit()

class Subcategory(db.Model):
    query_class = Query
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    entries = db.relationship('Entry', backref='subcategory', lazy='dynamic')

    def delete(self):
        for entry in self.entry:
            db.session.delete(entry)
        db.session.delete(self)
        db.session.commit()

    def __init__(self, name, id):
        category = Category.query.get(id)
        self.name = name
        self.category = category
        db.session.add(self)
        db.session.commit()  

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data

class Category(db.Model):
    query_class = Query
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True)
    subcategories = db.relationship('Subcategory', backref='category', lazy='dynamic')

    def delete(self):
        for subcategory in self.subcategories:
            subcategory.delete()
        db.session.delete(self)
        db.session.commit()

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data

    def __init__(self, name):
        self.name = name
        db.session.add(self)
        db.session.commit()    