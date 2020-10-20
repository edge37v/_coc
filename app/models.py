import re
import boto3
import base64, os, jwt
from time import time
from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from flask import jsonify, current_app, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

subscription_years = db.Table('subscription_years',
    db.Column('subscription_id', db.Integer, db.ForeignKey('subscription.id')),
    db.Column('year_id', db.Integer, db.ForeignKey('year.id')))

subscription_modules = db.Table('subscription_modules',
    db.Column('subscription_id', db.Integer, db.ForeignKey('subscription.id')),
    db.Column('module_id', db.Integer, db.ForeignKey('module.id')))

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page=1, per_page=10, endpoint='', **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'data': [item.to_dict() for item in resources.items]
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

class Subscription(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    year = db.relationship('Year', secondary=subscription_years, backref='subscription', lazy=True)
    module = db.relationship('Module', secondary=subscription_modules, backref='subscription', lazy=True)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)
    length = db.Column(db.Integer, default = 90)
    expires_in = db.Column(db.DateTime)

    def __repr__(self):
        return '{} {}'.format(self.year[0], self.module[0])

    def to_dict(self):
        data = {
            'year': self.year[0],
            'module': self.module[0]
        }
        return data

    def __init__(self, year, module):
        self.year.append(year)
        self.module.append(module)
        db.session.add(self)
        db.session.commit()

class Type(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

class Service(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    name = db.Column(db.Unicode)

    def __init__(self, user, name):
        self.user = user
        self.name = name
        db.session.add(self)
        db.session.commit()

class Product(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    name = db.Column(db.Unicode)

    def __init__(self, user, name):
        self.user = user
        self.name = name
        db.session.add(self)
        db.session.commit()

class Profile(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.Unicode)
    type = db.Column(db.Unicode)
    latitude = db.Column(db.Unicode)
    longitude = db.Column(db.Unicode)
    services = db.relationship('Service', backref='profile', lazy=True)
    products = db.relationship('Product', backref='profile', lazy=True)

    def __init__(self, user, name):
        self.user = user
        self.name = name
        db.session.add(self)
        db.session.commit()

    def service_exists(name):
        return Service.query.filter()

    def add_service(self, name):
        self.services.append(Service(self, name))
        db.session.commit()

    def add_product(self, name):
        self.products.append(Product(self, name))
        db.session.commit()

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

    def to_dict(self):
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

subscriptions  = db.Table('subscriptions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('subscription_id', db.Integer, db.ForeignKey('subscription.id')))

saved_profiles = db.Table('saved_profiles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('profile_id', db.Integer, db.ForeignKey('profile.id')))

saved_blogposts = db.Table('saved_blogposts',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('blogpost_id', db.Integer, db.ForeignKey('blogpost.id')))

saved_forumposts = db.Table('saved_forumposts',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('forumpost_id', db.Integer, db.ForeignKey('forumpost.id')))

class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscriptions = db.relationship('Subscription', secondary=subscriptions, backref='user', lazy='dynamic')
    ls = db.Column(db.Unicode)
    ly = db.Column(db.Unicode)
    profiles = db.relationship('Profile', backref='users', lazy='dynamic')
    l_access = db.Column(db.Boolean(), default=False)
    lesson_progress = db.Column(db.Unicode())
    saved_forumposts = db.relationship('Forumpost', secondary=saved_forumposts, backref=db.backref('them', lazy='dynamic'), lazy='dynamic')
    saved_blogposts = db.relationship('Blogpost', secondary=saved_blogposts, backref=db.backref('them', lazy='dynamic'), lazy='dynamic')
    saved_profiles = db.relationship('Profile', secondary=saved_profiles, backref=db.backref('them', lazy='dynamic'), lazy='dynamic')
    cards = db.relationship(Card, secondary=cards, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    logo_url = db.Column(db.Unicode)
    ads = db.relationship('Ad', backref='user', lazy='dynamic')
    customer_code = db.Column(db.Unicode)
    email = db.Column(db.Unicode(123), unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.Unicode(123))
    last_name = db.Column(db.Unicode(123))
    password_hash = db.Column(db.String(123))
    description = db.Column(db.Unicode(123))
    about = db.Column(db.UnicodeText())
    website = db.Column(db.String())
    phone = db.Column(db.String())
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    show_email = db.Column(db.Boolean, default=True)
    location = db.Column(db.String(347))
    token = db.Column(db.String(32), index=True, unique=True)
    #token_expiration = db.Column(db.DateTime)

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

    def to_dict(self):
        data = {
            'id': self.id,
            'email': self.email,
            'token': self.token
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about', 'confirmed', 'first_name', 'last_name', 'phone']:
            if field in data:
                setattr(self, field, data[field])
            if 'password' in data:
                self.set_password(data['password'])

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

lesson_subject = db.Table('lesson_subject',
    db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

lesson_year = db.Table('lesson_year',
    db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id'), primary_key=True),
    db.Column('year_id', db.Integer, db.ForeignKey('year.id'), primary_key=True)
)

lesson_module = db.Table('lesson_module',
    db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id'), primary_key=True),
    db.Column('module_id', db.Integer, db.ForeignKey('module.id'), primary_key=True)
)

class Lesson(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    s3_name = db.Column(db.Unicode())
    subject = db.relationship('Subject', secondary=lesson_subject, backref='lesson', lazy='dynamic')
    year = db.relationship('Year', secondary=lesson_year, backref='lesson', lazy='dynamic')
    module = db.relationship('Module', secondary=lesson_module, backref='lesson', lazy='dynamic')
    name = db.Column(db.Unicode(), unique=True)
    position = db.Column(db.Integer)
    desc = db.Column(db.Unicode)
    path = db.Column(db.Unicode)
    html = db.Column(db.Unicode)
    worksheet_path = db.Column(db.Unicode)
    video_url = db.Column(db.Unicode)
    worksheet_answers_path = db.Column(db.Unicode)

    @staticmethod
    def search(q, page, per_page):
        if '*' in q or '_' in q:
            _q = q.replace('_', '__')\
                .replace('*', '%')\
                .replace('?', '_')
        else:
            _q = '%{0}%'.format(q)
        r = Lesson.query.filter(Lesson.name.ilike(_q))
        return Lesson.to_collection_dict(r, page, per_page)

    def __init__(self, name, subject, year):
        #self.set_position(sci, position)
        db.session.add(self)
        self.name = name
        self.subject.append(subject)
        self.year.append(year)
        #self.module.append(module)
        #f = name.replace(' ', '_') + '.pdf'
        #self.s3_name = f
        db.session.commit()

    def set_position(self, subject, position):
        count = Lesson.query.join(lesson_subject, lesson_subject.c.subject_id == subject.id).count()
        if position is None:
            self.position = count+1
        if position > count:
                raise BaseException('Position is more than count')
        for i in range(position, count+1):
            l = Lesson.query.filter_by(position=i).first()
            if l:
                l.position = l.position+1
        self.postion = position

    def __repr__(self):
            return '{}'.format(self.name)
            
    def to_dict(self):
        data = {
            'id': self.id,
            's3_name': self.s3_name,
            'subject': self.subject.first().name,
            'year': self.year.first().name,
            'name': self.name,
            'desc': self.desc,
            'worksheet_path': self.worksheet_path,
            'video_url': self.video_url,
            'worksheet_answers_path': self.worksheet_answers_path,
        }
        return data

class Subject(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(3), unique=True)
    name = db.Column(db.String(123), unique=True)

    def to_dict(self):
        data = {
            'id': self.id,
            'sid': self.sid,
            'text': self.name
        }

        return data

    def __repr__(self):
            return '{}'.format(self.name)

class Year(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    sid = db.Column(db.String(3), unique=True)
    name = db.Column(db.String(123), unique=True)

    def to_dict(self):
        data = {
            'id': self.id,
            'sid': self.sid,
            'name': self.name
        }

        return data

    def __repr__(self):
            return '{}'.format(self.name)

class Module(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(3), unique=True)
    name = db.Column(db.String(123), unique=True)
    position = db.Column(db.Integer)

    def to_dict(self):
        data = {
            'id': self.id,
            'sid': self.sid,
            'name': self.name
        }

        return data

    def __repr__(self):
            return '{}'.format(self.name)