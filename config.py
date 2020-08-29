import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    PAK= 'sk_live_2567f775551d1f3e53665e529791d2e68072d213'
    SECRET_KEY='dev'
    USERS_PER_PAGE = 10
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGES = ['en', 'es']
    USERS_PER_PAGE = 10
    MAIL_SERVER= 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'edge3769@gmail.com'
    MAIL_PASSWORD = 'loveGM1!'
    ADMINS = ['edge2347@gmail.com']