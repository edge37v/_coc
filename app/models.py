from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy_searchable import SearchQueryMixin, make_searchable
from sqlalchemy_utils.types import TSVectorType
import base64, os, jwt
from time import time
from flask import jsonify, current_app, request, url_for
from app import db, login
from flask_login import UserMixin, AnonymousUserMixin
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

class UserQuery(BaseQuery, SearchQueryMixin):
    pass

class User(PaginatedAPIMixin, UserMixin, db.Model):
        query_class = UserQuery
        #search_vector = db.Column(TSVectorType('description', 'name'))
        id = db.Column(db.Integer, primary_key=True)
        ps_id = db.Column(db.Integer)
        ps_code = db.Column(db.String())
        ps_email = db.Column(db.Unicode())
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

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ps_id = db.Column(db.Integer)
    name = db.Column(db.Unicode())
    amount = db.Column(db.Unicode())
    period = db.Column(db.Unicode())

    def from_dict(self, data):
            for field in ['name', 'amount', 'period']:
                if field in data:
                    setattr(self, field, data[field])