from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import _37, blog, forums, auth, users, errors, paystack, tokens, learn