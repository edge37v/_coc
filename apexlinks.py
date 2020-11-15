from app import create_app, db
from flask import jsonify
from app.blog_models import Blog, Blogpost
from app.forum_models import Forum, Forumpost
from app.models import User, Field, Card, Service, Product, Location

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'Field': Field, 'db': db, 'User': User, 'Location': Location, 'jsonify': jsonify, 'Forumpost': Forumpost, 'Product': Product, \
        'location': Location.query.get(1), 'user': User.query.get(1), 'Blog': Blog, 'Blogpost': Blogpost, 'Service': Service}