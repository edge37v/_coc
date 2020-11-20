from app import db
from flask import jsonify
from sqlalchemy_utils.types import TSVectorType
from app.models import PageMixin, Query, User, cdict

s_class_categories = db.Table('s_class_categories',
    db.Column('s_category_id', db.Integer, db.ForeignKey('s_category.id')),
    db.Column('s_class_id', db.Integer, db.ForeignKey('s_class.id')))

service_categories = db.Table('service_categories',
    db.Column('s_category_id', db.Integer, db.ForeignKey('s_category.id')),
    db.Column('service_id', db.Integer, db.ForeignKey('service.id')))

class SCategory(PageMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    json = db.Column(db.JSON)
    fields = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    classes = db.relationship('SClass', secondary=s_class_categories, backref='categories', lazy=True)
    services = db.relationship('Service', secondary=service_categories, backref='categories', lazy=True)

    def __init__(self, name, token, fields={}, json={}):
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        self.user = user
        self.name = name
        self.json = json
        self.fields = fields
        db.session.add(self)
        db.session.commit()

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'json': self.json,
            'fields': self.fields
        }
        return data

    @staticmethod
    def service_added(s_category, service):
        return service.categories.filter(
            service_categories.c.s_category_id == s_category.id
        ).count()>0

    @staticmethod
    def add_service(service_id, s_category_id, token):
        errors = []
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        s_category = SCategory.query.get(s_category_id)
        service = Service.query.get(service_id)
        if s_category.user != user or service.user != user:
            return {}, 401
        if service_added(s_category, service):
            errors.append('Already added to category')
            return {'errors': errors}
        s_category.servicees.append(service)
        db.session.commit()

    @staticmethod
    def remove_service(service_id, s_category_id, token):
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        s_category = SCategory.query.get(service_id)
        service = Service.query.get(s_category_id)
        if s_category.user !=user and service.user !=user:
            return {}, 401
        if not service_added(s_category, service):
            errors.append('Not a member of class')
            return {'errors': errors}


    @staticmethod
    def s_class_added(s_category, s_class):
        return s_class.categories.filter(
            s_class_categories.c.s_category_id == s_category.id
        ).count()>0

    @staticmethod
    def add_s_class(s_class_id, s_category_id, token):
        errors = []
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        s_category = SCategory.query.get(s_category_id)
        s_class = SClass.query.get(s_class_id)
        if s_category.user != user or s_class.user != user:
            return {}, 401
        if s_class_added(s_category, s_class):
            errors.append('Already added to category')
            return {'errors': errors}
        s_category.s_classes.append(s_class)
        db.session.commit()

    @staticmethod
    def remove_s_class(s_class_id, s_category_id, token):
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        s_category = SCategory.query.get(service_id)
        s_class = SClass.query.get(s_category_id)
        if s_category.user !=user and s_class.user !=user:
            return {}, 401
        if not s_class_added(s_category, s_class):
            errors.append('Not a member of class')
            return {'errors': errors}

    @staticmethod
    def edit(id, token, *args):
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        s_category = SCategory.query.get(id)
        if s_category.user != user:
            return {}, 401
        if name in args:
            s_category.name = name
        if json in args:
            s_category.json = json
        db.session.commit()

    @staticmethod
    def delete(ids, token):
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        for id in ids:
            s_category = SCategory.query.get(id)
            if s_category.user != user:
                return {}, 401
            db.session.delete(s_category)
            db.session.commit()

class SClass(PageMixin, db.Model):
    query_class = Query
    search_vector = db.Column(TSVectorType('name'))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    fields = db.Column(db.JSON)
    archived = db.Column(db.Boolean, default=False)
    services = db.relationship('Service', backref='s_class', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    paid_in = db.Column(db.Unicode)

    def search(q):
        if '*' in q or '_' in q:
            _q = q.replace('_', '__')\
                .replace('_', '__')\
                .replace('*', '%')\
                .replace('?', '_')
        else:
            _q = '%{0}%'.format(q)
        q1 = SClass.query.filter(SClass.name.ilike(_q))
        #q2 = SClass.query.search('"' + q + '"', sort=True)
        #s_classes = q1.union(q2)
        return jsonify([{'id': s.id, 'text': s.name} for s in q1])

    def __init__(self, json, token, name, fields, paid_in):
        user = User.query.filter_by(token = token).first()
        self.user = user
        self.name = name
        self.fields = fields
        self.paid_in = paid_in
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def archive(ids, token):
        user = User.query.filter_by(token=token).first()
        for id in ids:
            s_class = SClass.query.get(id)
            if s_class.user == user:
                s_class.archived = True
        db.session.commit()
        return {}, 202

    @staticmethod
    def unarchive(ids, token):
        user = User.query.filter_by(token=token).first()
        for id in ids:
            s_class = SClass.query.get(id)
            if s_class.user == user:
                s_class.archived = False
        db.session.commit()
        return {}, 202


    @staticmethod
    def added(service, s_class):
        return service.s_class == s_class

    @staticmethod
    def add(token, service_id, s_class_id):
        errors = []
        user = User.query.filter_by(token=token).first()
        service = Service.query.get(service_id)
        s_class = SClass.query.get(s_class_id)
        if service.user != user and s_class.user != user:
            return {}, 401
        if added(service, s_class):
            errors.append('Service ' + service.name + ' already added to class')
            return {'errors': errors}
        s_class.services.append(service)
        db.session.commit()

    @staticmethod
    def remove(token, service_id, s_class_id):
        user = User.query.filter_by(token=token).first()
        service = Service.query.get(service_id)
        s_class = SClass.query.get(s_class_id)
        if service.user != user and s_class.user != user:
            return {}, 401
        s_class.services.remove(service)
        db.session.commit()

    @staticmethod
    def edit(id, token, name, fields, paid_in):
        user = User.query.filter_by(token = token).first()
        service = Service.query.get(id)
        if service.user != user:
            return {}, 401
        service.name = name
        service.fields = fields
        service.paid_in = paid_in
        db.session.commit()

    @staticmethod
    def delete(ids, token):
        user = User.query.filter_by(token=token).first()
        for id in ids:
            s_class = SClass.query.get(id)
            if s_class.user == user:
                db.session.delete(s_class)
        db.session.commit()

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'fields': self.fields,
            'services': cdict(self.services)
        }
        return data

class Service(PageMixin, db.Model):
    query_class = Query
    search_vector = db.Column(
        TSVectorType(
            'name', 'about', weights={'name': 'A', 'about': 'B'}))
    id = db.Column(db.Integer, primary_key=True)
    s_class_id = db.Column(db.Integer, db.ForeignKey('s_class.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('s_category.id'))
    archived = db.Column(db.Boolean, default=False)
    viewed = db.Column(db.JSON)
    price = db.Column(db.Unicode)
    fields = db.Column(db.JSON)
    json = db.Column(db.JSON)
    name = db.Column(db.Unicode)
    about = db.Column(db.Unicode)
    paid_in = db.Column(db.Unicode)

    @staticmethod
    def archive(id, token):
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        service = Service.query.get(id)
        if service.user != user:
            return {'errors': ['Service does not belong to user']}
        service.archived = True
        db.session.commit()

    @staticmethod
    def unarchive(id, token):
        errors = []
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        service = Service.query.get(id)
        if service.user != user:
            return {'errors': ['Service does not belong to user']}
        service.archived = False
        db.session.commit()
        return {}, 201

    @staticmethod
    def saved(user, service):
        return user.saved_services.filter(saved_services.c.service_id == service.id).count()>0

    @staticmethod
    def save(id, token):
        errors = []
        user = User.query.filter_by(token=token).first()
        service = Service.query.get(id)
        if saved(user, service):
            errors.append('Service ' + service.name + ' was already saved')
            return {'errors': errors}
        user.saved_services.append(service)
        db.session.commit()
        return {}, 201

    @staticmethod
    def unsave(id, token):
        errors = []
        user = User.query.filter_by(token=token).first()
        service = Service.query.get(id)
        if not saved(user, service):
            errors.append("Service wasn't saved before")
            return {'errors': errors}
        user.saved_services.remove(service)
        db.session.commit()
        return {}, 201

    @staticmethod
    def search(q, filters=[], s_page=1, p_page=1):
        if '*' in q or '_' in q:
            _q = q.replace('_', '__')\
                .replace('_', '__')\
                .replace('*', '%')\
                .replace('?', '_')
        else:
            _q = '%{0}%'.format(q)
        #n = User.query.filter(User.name.ilike(_q))
        #e = User.query.filter(User.email.ilike(_q))
        #p = User.query.filter(User.phone.ilike(_q))
        #users = cdict(u, page, 37)
        services = Service.query.search('"' + _q + '"', sort=True)
        products = Product.query.filter(Product.name.ilike(_q))
        #q = n.union(e).union(p)
        #u = User.query.filter(User.location.any(name=location))
        servs = cdict(services, s_page, 37)
        prods = cdict(products, p_page, 37)
        data = {
            'services': servs,
            'products': prods,
        }
        return jsonify(data)

    def dict(self):
        data = {
            'id': self.id,
            'json': self.json,
            'name': self.name,
            'about': self.about,
            'user': self.user.dict(),
            'paid_in': self.paid_in
        }
        if self.s_class:
            data['s_class'] = self.s_class.dict()
        return data

    @staticmethod
    def exists(user, name):
        return Service.query.filter_by(user_id = user.id).count()>0

    def __init__(self, json, token, name, s_class_id, fields, about, price, paid_in):
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        s_class = SClass.query.get(id)
        self.user = user
        self.name = name
        self.s_class = s_class
        self.fields = fields
        self.about = about
        self.paid_in = paid_in
        self.price = price
        self.json = json
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def edit(id, token, name, json):
        user = User.query.filter_by(token=token).first()
        service = Service.query.get(id)
        if service.user == user:
            service.name = name
            service.json = json
            db.session.add(service)
            db.session.commit()
            return service
        return {}, 401

    @staticmethod
    def delete(id, token):
        user = User.query.filter_by(token=token).first()
        service = Service.query.get(id)
        if service.user == user:
            db.session.delete(service)
            db.session.commit()
