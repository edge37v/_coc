import random
from app import db
from app.models import PaginatedAPIMixin

class Ad(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Unicode)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, url):
        self.url = url
        db.session.add(self)

    @staticmethod
    def get():
        a = Ad.query.count()
        id = random.randrange(1, a)
        ad = Ad.query.get(id)
        return ad.url
