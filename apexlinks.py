from app import create_app, db
from app.ad_models import Ad
from flask import jsonify
from app._37m import Text
from app.blog_models import Blog, Blogpost
from app.forum_models import Forum, Forumpost
from app.models import Subscription, Year, Subject, Module, Lesson, User, Card

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'jsonify': jsonify, 'Subscription': Subscription, 'Year': Year, 'Forumpost': Forumpost, \
        'u': User.query.get(1), 'Blog': Blog, 'Text': Text, 'Blogpost': Blogpost, \
        's': Subscription.query.get(1), 'Forum': Forum, \
        'Subject': Subject, 'Module': Module, 'Card': Card, \
        'Lesson': Lesson, 'db': db, 'User': User, 'Ad': Ad, \
        'yr1': Year.query.get(1), 'yr2': Year.query.get(2), \
        'yr3': Year.query.get(3), 'yr4': Year.query.get(4), \
        'yr5': Year.query.get(5), 'yr6': Year.query.get(6), \
        'sci': Subject.query.filter_by(sid='sci').first(), \
        'mth': Subject.query.filter_by(sid='mth').first(), \
        'eng': Subject.query.filter_by(sid='eng').first(), \
        'md1': Module.query.filter_by(sid='md1').first(), \
        'md2': Module.query.filter_by(sid='md2').first(), \
        'md3': Module.query.filter_by(sid='md3').first(), \
        'md4': Module.query.filter_by(sid='md4').first()}


