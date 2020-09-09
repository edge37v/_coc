from app import create_app, db
from app.models import Year, Subject, Level, Module, Lesson, User, Card, LPlan

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'Year': Year, 'Subject': Subject, 'Level': Level, \
        'Module': Module, 'Lesson': Lesson, 'db': db, \
        'User': User, 'Card': Card, 'LPlan': LPlan, \
        'yr1': Year.query.get(1), 'yr2': Year.query.get(2), \
        'yr3': Year.query.get(3), 'yr4': Year.query.get(4), \
        'yr5': Year.query.get(5), 'yr6': Year.query.get(6), \
        'sci': Subject.query.filter_by(sid='sci').first(), \
        'mth': Subject.query.filter_by(sid='mth').first(), \
        'eng': Subject.query.filter_by(sid='eng').first(), \
        'trn': Module.query.filter_by(sid='trn').first(), \
        'win': Module.query.filter_by(sid='win').first(), \
        'spg': Module.query.filter_by(sid='spg').first(), \
        'sum': Module.query.filter_by(sid='sum').first(), \
        'bgn': Level.query.filter_by(sid='bgn').first(), \
        'prg': Level.query.filter_by(sid='prg').first(), \
        'ult': Level.query.filter_by(sid='ult').first()}

#l_monthly
#l_yearly


