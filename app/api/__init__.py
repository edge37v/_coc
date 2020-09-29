from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

from app.api import blog, forums, auth, main, users, errors, paystack, tokens, learning