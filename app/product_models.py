from app import db
from app.models import PageMixin

class Brand(PageMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)

class Shoe(PageMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    brand = db.Column(db.Unicode)
    size = db.Column(db.Integer)
    material = db.Column(db.Unicode)
    colors = db.Column(db.JSON)

  