from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy_searchable import SearchQueryMixin, make_searchable
from sqlalchemy_utils.types import TSVectorType
import base64, os, jwt
from time import time
from flask import jsonify, current_app, request, url_for
from app import db, login
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            'meta': {
                'page': page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page, 
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
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

class Lplan(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ps_id = db.Column(db.Integer())
    name = db.Column(db.Unicode())
    amount = db.Column(db.Unicode())
    period = db.Column(db.Unicode())

    def to_dict(self):
        data = {
            'id': self.id,
            'ps_id': self.ps_id,
            'name': self.name,
            'amount': self.amount,
            'period': self.period
        }
        return data

user_lplans = db.Table('user_lplans',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('lplan_id', db.Integer, db.ForeignKey('lplan.id')))

class UserQuery(BaseQuery, SearchQueryMixin):
    pass

class User(PaginatedAPIMixin, UserMixin, db.Model):
        query_class = UserQuery
        #search_vector = db.Column(TSVectorType('description', 'name'))
        id = db.Column(db.Integer, primary_key=True)
        ps_id = db.Column(db.Integer)
        ps_code = db.Column(db.String())
        ps_email = db.Column(db.Unicode())
        lplans = db.relationship('LPlan', secondary=user_lplans, backref=db.backref('users', lazy=True), lazy=True)
        lesson_progress = db.Column(db.Unicode())
        cards = db.relationship(Card, backref='user', lazy='dynamic')
        logo_url = db.Column(db.String())
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
        token_expiration = db.Column(db.DateTime)

        def get_token(self, expires_in=3600):
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
            return '<user {}>'.format(self.email)

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

        def to_dict(self, include_email=False):
            data = {
                'id': self.id,
                'confirmed': self.confirmed,
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'phone': self.phone,
                'about': self.about,
                '_links': {
                    'self': url_for('api.get_user', id = self.id)
                }
            }
            if include_email:
                data['email'] = self.email
            return data

        def from_dict(self, data, new_user=False):
            for field in ['username', 'email', 'about', 'confirmed', 'first_name', 'last_name', 'phone']:
                if field in data:
                    setattr(self, field, data[field])
                if 'password' in data:
                    self.set_password(data['password'])

class MPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ps_id = db.Column(db.Integer)
    name = db.Column(db.Unicode())
    amount = db.Column(db.Unicode())
    period = db.Column(db.Unicode())

    def to_dict(self)
        data = {
            'id': self.id,
            'ps_id': self.ps_id,
            'name': self.name,
            'amount': self.amount,
            'period': self.period
        }

    def from_dict(self, data):
            for field in ['name', 'amount', 'period']:
                if field in data:
                    setattr(self, field, data[field])

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

lesson_level = db.Table('lesson_level',
    db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id'), primary_key=True),
    db.Column('level_id', db.Integer, db.ForeignKey('level.id'), primary_key=True)
)

class Lesson(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.relationship('Subject', secondary=lesson_subject, backref='lesson', lazy='dynamic')
    year = db.relationship('Year', secondary=lesson_year, backref='lesson', lazy='dynamic')
    module = db.relationship('Module', secondary=lesson_module, backref='lesson', lazy='dynamic')
    level = db.relationship('Level', secondary=lesson_level, backref='lesson', lazy='dynamic')
    name = db.Column(db.Unicode(), unique=True)
    position = db.Column(db.Integer)
    desc = db.Column(db.Unicode())
    url = db.Column(db.Unicode())
    worksheet_url = db.Column(db.Unicode())
    video_url = db.Column(db.Unicode())
    worksheet_answers_url = db.Column(db.Unicode())

    def __repr__(self):
            return '<Lesson {}>'.format(self.name)
            
    def to_dict(self):
        data = {
            'id': self.id,
            'url': self.url,
            'subject': self.subject,
            'year': self.year,
            'position': self.position,
            'module': self.module,
            'level': self.level,
            'name': self.name,
            'desc': self.desc,
            'worksheet_url': self.worksheet_url,
            'video_url': self.video_url,
            'worksheet_answers_url': self.worksheet_answers_url
        }

        return data

    def createl_url(self):
        s = Subject.query.join(lesson_subject, (lesson_subject.c.lesson_id == self.id)).first()
        y = Year.query.join(lesson_year, (lesson_year.c.lesson_id == self.id)).first()
        m = Module.query.join(lesson_module, (lesson_module.c.lesson_id == self.id)).first()
        l = Level.query.join(lesson_level, (lesson_level.c.lesson_id == self.id)).first()
        self.url = 'lessons' + '/' + str(s.sid) + '/' + str(y.sid) + '/' + str(m.sid) + '/' + str(l.sid) + '/' + str(self.name) + '.svg'

class Subject(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
            return '<Subject {}>'.format(self.name)

class Year(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
            return '<Grade {}>'.format(self.name)

class Module(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
            return '<Module {}>'.format(self.name)

class Level(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
            return '<Level {}>'.format(self.name)