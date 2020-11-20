from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import s_categories, s_classes, main, products, services, blog, forums, auth, users, errors, location, tokens