user_lplans = db.Table('user_lplans',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('lplan_id', db.Integer, db.ForeignKey('lplan.id')))

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

    def __repr__(self):
            return '<Level {}>'.format(self.name)

class LPlan(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ps_id = db.Column(db.Integer)
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