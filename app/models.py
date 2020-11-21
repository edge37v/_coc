import re
import boto3
import base64, os, jwt
from time import time
from app import db
from flask import jsonify
from geopy import distance
from flask_login import UserMixin
from datetime import datetime, timedelta
from flask_sqlalchemy import BaseQuery
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import make_searchable
from flask import jsonify, current_app, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.search import add_to_index, remove_from_index, query_index

class Query(BaseQuery, SearchQueryMixin):
    pass

class SearchMixin(object):
    @classmethod
    def search(cls, expression, page):
        ids, total = query_index(cls.__tablename__, expression, page, 37)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.to_cdict(cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)))

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.configure_mappers()
db.event.listen(db.session, 'before_commit', SearchMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchMixin.after_commit)

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

class PageMixin(object):
    @staticmethod
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

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Unicode)

    def __init__(self, text):
        self.text = text
        db.session.add(self)
        db.session.commit()

    def dict(self):
        data = {
            'id': self.id,
            'text': self.text
        }
        return data

    @staticmethod
    def search(q):
        if '*' in q or '_' in q:
            _q = q.replace('_', '__')\
                .replace('_', '__')\
                .replace('*', '%')\
                .replace('?', '_')
        else:
            _q = '%{0}%'.format(q)
        return Field.query.filter(Field.text.ilike(_q))

class Place(db.Model):
    query_class = Query
    search_vector = db.Column(TSVectorType('name'))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    location = db.Column(db.JSON)

    @staticmethod
    def search(q):
        if '*' in q or '_' in q:
            _q = q.replace('_', '__')\
                .replace('_', '__')\
                .replace('*', '%')\
                .replace('?', '_')
        else:
            _q = '%{0}%'.format(q)
        return Place.query.filter(Place.name.ilike(_q))

    def dict(self):
        data = {
            'id': self.id,
            'text': self.name
        }
        return data

    def __init__(self, name, location):
        self.name = name
        self.location = location
        db.session.add(self)
        db.session.commit()

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Product(PageMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    json = db.Column(db.JSON) 
    name = db.Column(db.Unicode)
    about = db.Column(db.Unicode)

    def dict(self):
        data = {
            'id': self.id,
            'json': self.json,
            'name': self.name,
            'about': self.about,
            'user': self.user.dict()
        }
        return data

    @staticmethod
    def exists(user, name):
        return Product.query.filter_by(user_id = user.id).count()>0

    def __init__(self, json, id, name):
        user = User.query.get(id)
        self.user = user
        self.name = name
        self.json = json
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def delete(id):
        db.session.delete(Service.query.get(id))

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    authorization_code = db.Column(db.Unicode())
    card_type = db.Column(db.Unicode())
    last4 = db.Column(db.Unicode())
    exp_month = db.Column(db.Unicode())
    exp_year = db.Column(db.Unicode())
    bin = db.Column(db.Unicode())
    bank = db.Column(db.Unicode())
    signature = db.Column(db.Unicode())
    reusable = db.Column(db.Boolean())
    country_code = db.Column(db.Unicode())

    def dict(self):
        data = {
            'user_id': self.user_id,
            'authorizatiion_code': self.authorization_code,
            'card_type': self.card_type,
            'signature': self.signature,
            'last4': self.last4,
            'exp_month': self.exp_month,
            'exp_year': self.exp_year,
            'bin': self.bin,
            'bank': self.bank,
            'signature': self.signature,
            'reusable': self.reusable,
            'country_code': self.country_code,
        }
        return data

    def from_dict(self, data):
        for field in ['authorization_code', 'card_type', 'last4', 'exp_month', 'exp_year', 'bin', 'bank', 'signature', 'reusable', 'country_code']:
            setattr(self, field, data[field])

cards = db.Table('cards',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('card_id', db.Integer, db.ForeignKey('card.id')))

saved_users = db.Table('saved_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')))

saved_services = db.Table('saved_services',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('service', db.Integer, db.ForeignKey('service.id')))

saved_products = db.Table('saved_products',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('product', db.Integer, db.ForeignKey('product.id')))

saved_blogposts = db.Table('saved_blogposts',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('blogpost_id', db.Integer, db.ForeignKey('blogpost.id')))

saved_forumposts = db.Table('saved_forumposts',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('forumpost_id', db.Integer, db.ForeignKey('forumpost.id')))

class User(PageMixin, UserMixin, db.Model):
    __searchable__ = ['name', 'email', 'phone', ]
    id = db.Column(db.Integer, primary_key=True)
    ls = db.Column(db.Unicode)
    ly = db.Column(db.Unicode)
    tokens = db.relationship(Token, backref='user', lazy='dynamic')
    l_access = db.Column(db.Boolean(), default=False)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    location = db.Column(db.JSON)
    openby = db.Column(db.DateTime)
    closeby = db.Column(db.DateTime)

    s_categories = db.relationship('SCategory', backref='user', lazy='dynamic')
    s_classes = db.relationship('SClass', backref='user', lazy='dynamic')
    
    services = db.relationship('Service', backref='user', lazy='dynamic')
    products = db.relationship('Product', backref='user', lazy='dynamic')
    
    saved_users = db.relationship('User', secondary=saved_users, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    saved_services = db.relationship('Service', secondary=saved_services, backref='savers', lazy='dynamic')
    saved_products = db.relationship('Product', secondary=saved_products, backref='savers', lazy='dynamic')
    
    saved_forumposts = db.relationship('Forumpost', secondary=saved_forumposts, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    saved_blogposts = db.relationship('Blogpost', secondary=saved_blogposts, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    cards = db.relationship(Card, secondary=cards, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    distance = db.Column(db.Unicode)
    logo_url = db.Column(db.Unicode)
    customer_code = db.Column(db.Unicode)
    email = db.Column(db.Unicode(123), unique=True)

    visible = db.Column(db.Boolean, default=False)
    
    name = db.Column(db.Unicode(123))
    password_hash = db.Column(db.String(123))
    description = db.Column(db.Unicode(123))
    about = db.Column(db.UnicodeText())
    website = db.Column(db.String())
    phone = db.Column(db.String())
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    show_email = db.Column(db.Boolean, default=True)
    token = db.Column(db.String(373), index=True, unique=True)
    marketlnx = db.Column(db.Boolean, default=False)

    def set_distance(self, distance):
        self.distance = distance
        db.session.add(self)
        db.session.commit()

    def edit_location(self, lat, lon):
        self.longitude = lon
        self.latitude = lat
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def distance(lat, lon, e2):
        e1 = (lat, lon)
        e2 = (e2.lat, e2.lon)
        return distance.distance(e1, e2).miles

    @staticmethod
    def sort(lat, lon, query):
        for i in range(1, query.count()+1):
            user = User.query.get(i)
            user.set_distance(User.distance(lat, lon, user))
        return query.order_by(User.distance.desc())  

    """def get_token(self, expires_in=36000):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user
    """

    def __init__(self, email, password):
        self.email=email
        self.set_password(password)
        db.session.add(self)
        db.session.commit()

    def get_utoken(self, expires_in=600):
        return jwt.encode(
            {'confirm_account': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def check_utoken(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['confirm_account']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return 'email: {}'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def add_service(id, name):
        user = User.query.get(id)
        Service(user, name)

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'token': self.token
        }
        if self.location == None:
            data['location'] = self.location.first().name
        return data

    def qdict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'about': self.about,
            'website': self.website,
            'token': self.token,
            'saved_users': cdict(self.saved_users),
            'saved_services': cdict(self.saved_services),
            'services': cdict(self.services),
            'products': cdict(self.products)
        }
        if self.location == None:
            data['location'] = self.location.first().name
        return data

    def from_dict(self, data):
        self.email = data['email']
        self.name = data['name']
        self.about = data['about']
        self.phone = data['phone']
        self.website = data['website']
        self.location = data('location')
        if 'password' in data:
            self.set_password(data['password'])
        db.session.add(self)
        db.session.commit()

    def add_card(self, card):
        if not self.has_card(card):
            self.cards.append(card)

    def remove_card(self, card):
        if self.has_card(card):
            self.remove(card)

    def has_card(self, card):
        return self.cards.filter(
            cards.c.card_id == card.id).count() > 0

    def subscribe(self, year, module):
        s=Subscription(year, module)
        self.subscriptions.append(s)
        db.session.commit()

    def unsubscribe(self, year, module):
        s=Subscription(year, module)
        self.subscriptions.remove(s)
        db.session.commit()

    def subscribed(self, year, module):
        return self.subscriptions.filter(
            subscriptions.c.subscription_id == s.id).count()>0