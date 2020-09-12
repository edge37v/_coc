import re
import base64, os, jwt
from time import time
from app import db, login
from pypaystack import Plan
from flask_login import UserMixin
from datetime import datetime, timedelta
basedir = os.path.abspath(os.path.dirname(__file__))
from flask import jsonify, current_app, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

subscription_modules = db.Table('subscription_modules',
    db.Column('module_id', db.Integer, db.ForeignKey('module.id')),
    db.Column('module_id', db.Integer, db.ForeignKey('module.id')))

subscription_years = db.Table('subscription_years',
    db.Column('year_id', db.Integer, db.ForeignKey('year.id')),
    db.Column('module_id', db.Integer, db.ForeignKey('module.id')))

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page=1, per_page=10, endpoint='', **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {'items': [item.to_dict() for item in resources.items]}
        if page:
            data['meta'] = {
                'page': page,
                'total_pages': resources.pages,
                'total_items': resources.total
            }
        if endpoint:
            data['_links'] = {
                'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page, 
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        return data

class Subscription(PaginatedMixin, db.Model):
    year = db.relationship('Year', secondary=subscription_years, backref='subscription', lazy=True)
    module = db.relationship('Module', secondary=subscription_modules, backref='subscription', lazy=True)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)
    length = db.Column(db.Integer, default = 90)
    expires_in = db.Column(db.DateTime)

    def __init__(year, module):
        year = Year.query.filter_by(name=year).first()
        module = Module.query.filter_by(name=module).first()
        self.year.append(year)
        self.module.append(module)
        self.expires_in = self.timestamp + timedelta(days = self.length)
        db.session.add(self)
        db.session.commit()


l_plan_services = db.Table('l_plan_services',
    db.Column('l_plan_id', db.Integer, db.ForeignKey('l_plan.id')),
    db.Column('service_id', db.Integer, db.ForeignKey('service.id')))

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Unicode())
    name = db.Column(db.Unicode())

class LPlan(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ps_id = db.Column(db.Integer())
    name = db.Column(db.Unicode())
    amount = db.Column(db.Integer)
    year = db.Column(db.Unicode)
    interval = db.Column(db.Unicode())
    service = db.relationship(Service, secondary=l_plan_services, backref='l_plan', lazy='dynamic')

    def __init__(self, name, amount, interval):
        p = Plan()
        p.create(name=name, amount=amount, interval=interval)
        self.name = name
        self.amount = amount
        self.interval = interval
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return 'Plan {}: {}'.format(self.id, self.name)

    def to_dict(self):
        data = {
            'id': self.id,
            'ps_id': self.ps_id,
            'name': self.name,
            'year': self.year,
            'amount': self.amount,
            'interval': self.interval,
        }
        return data

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

user_cards = db.Table('user_cards',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('card_id', db.Integer, db.ForeignKey('card.id')))

user_l_plans = db.Table('user_l_plans',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('l_plan_id', db.Integer, db.ForeignKey('l_plan.id')))

user_services = db.Table('user_services',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('service_id', db.Integer, db.ForeignKey('service.id')))

user_subscriptions  = db.Table('user_subscriptions',
    db.Column('subscription_id', db.Integer, db.ForeignKey('subscription.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')))

class User(PaginatedAPIMixin, UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        ps_id = db.Column(db.Integer)
        ps_code = db.Column(db.String())
        ps_email = db.Column(db.Unicode())
        subscriptions = db.relationship('Subscription', secondary=user_subscriptions, backref='user')
        l_plans = db.relationship('LPlan', secondary=user_l_plans, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
        services = db.relationship('Service', secondary=user_services, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
        l_access = db.Column(db.Boolean(), default=False)
        lesson_progress = db.Column(db.Unicode())
        cards = db.relationship(Card, secondary=user_cards, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
        logo_url = db.Column(db.Unicode)
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
        token_expiration = db.Column(db.DateTime)

        def __init__(email, password):
            self.email = 'email'
            self.set_password(password)
            db.session.add(self)
            db.session.commit()

        def get_token(self, expires_in=36000):
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
            return 'email: {}'.format(self.email)

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

        def to_dict(self, include_email=False):
            l = list(self.l_plans)
            def get_l(l):
                for i in range(len(l)):
                    return {'plan': str(l[i])}
            data = {
                'id': self.id,
                'confirmed': self.confirmed,
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'phone': self.phone,
                'about': self.about,
                'password': 'love',
                #'_links': {
                #    'self': url_for('api.get_user', id = self.id)
                #},
                'l_plans': get_l(l)
            }
            #if include_email:
            #    data['email'] = self.email
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
                user_cards.c.card_id == card.id).count() > 0

        def subscribe(self, year, module):
            s=Subscription(year, module)
            self.subscriptions.append(s)
            db.session.commit()

        def unsubscribe(self, l_plan):
            pass

        def subscribed(self, l_plan):
            pass

        def gets_service(self, service):
            return self.service.filter(
                user_services.c.service_id == service.id).count() > 0

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
    path = db.Column(db.Unicode())
    worksheet_path = db.Column(db.Unicode())
    video_url = db.Column(db.Unicode())
    worksheet_answers_path = db.Column(db.Unicode())

    def __init__(self, name, subject, year, module, level):
        self.name = name
        self.subject.append(subject)
        self.year.append(year)
        self.module.append(module)
        self.level.append(level)
        s = subject.sid
        y = year.sid
        m = module.sid
        l = level.sid
        f = name.replace(' ', '_')
        filename = f + '.pdf'
        location = 'lessons' + '\\' + s + '\\' + y + '\\' + m + '\\' + l
        file_path = os.path.join(location, filename)
        base_path = os.path.join(basedir, 'static\\' + location)
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        path = os.path.join(base_path, filename)
        self.path = file_path
        l = open(path, 'w+')
        l.close()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
            return 'name: {}'.format(self.name)
            
    def to_dict(self):
        data = {
            'id': self.id,
            'path': self.path,
            'subject': self.subject.first().name,
            'year': self.year.first().name,
            'module': self.module.first().name,
            'level': self.level.first().name,
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
            'name': self.name
        }

        return data

    def __repr__(self):
            return 'name {}'.format(self.name)

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
            return 'name {}'.format(self.name)

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
            return 'name {}'.format(self.name)

class Level(PaginatedAPIMixin, db.Model):
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
            return 'name: {}'.format(self.name)