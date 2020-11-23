from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import s_categories, s_classes, products, services, blog, forums, fields, auth, users, errors, places, tokens