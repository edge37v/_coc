import os, logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from elasticsearch import Elasticsearch
from flask_moment import Moment
from config import Config
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask import Flask, url_for, request
from algoliasearch.search_client import SearchClient
basedir = os.path.abspath(os.path.dirname(__file__))
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
babel = Babel()
moment = Moment()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = ('You gotta login first')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    babel.init_app(app)
    moment.init_app(app)
    login.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .user import bp as user_bp
    app.register_blueprint(user_bp)

    from .pages import bp as pages_bp
    app.register_blueprint(pages_bp)

    from .models import User

    return app

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Marketlnx Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
        )

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/marketlnx.log', maxBytes=1024,
                                        backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    applogger.info('Marketlnx startup')

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])