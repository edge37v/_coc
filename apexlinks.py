from app import create_app, db
from app.models import Year, Subject, Module, Lesson, User, Card

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'Year': Year, 'Subject': Subject, \
        'Module': Module, 'Lesson': Lesson, 'db': db, \
        'User': User, 'Card': Card, \
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


