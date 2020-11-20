from flask import jsonify
from app import create_app, db
from app.service_models import Service
from app.blog_models import Blog, Blogpost
from app.forum_models import Forum, Forumpost
from app.models import User, Field, Card, Product, Location

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'Field': Field, 'db': db, 'User': User, 'Location': Location, 'jsonify': jsonify, 'Forumpost': Forumpost, 'Product': Product, \
        'Blog': Blog, 'Blogpost': Blogpost, 'Service': Service}