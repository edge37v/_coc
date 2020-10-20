from app import db
from datetime import datetime
from app.models import PaginatedAPIMixin

class Text(PaginatedAPIMixin, db.Model):
    time = db.Column(db.DateTime, default=datetime.utcnow)
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Unicode(37))

    def __init__(self, body):
        self.body = body
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        data = {
            'id': self.id,
            'time': self.time,
            'body': self.body
        }
        return data

    @staticmethod
    def search(q, page, per_page):
        if '*' in q or '_' in q:
            _q = q.replace('_', '__')\
                .replace('*', '%')\
                .replace('?', '_')
        else:
            _q = '%{0}%'.format(q)
        r = Text.query.filter(Text.body.ilike(_q))
        return Text.to_collection_dict(r, page, per_page)


