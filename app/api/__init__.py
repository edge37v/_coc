from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import main, products, productgroups, services, blog, forums, auth, users, errors, location, tokens