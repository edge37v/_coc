from app import create_app, db
from app.models import User, Card, Plan

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Card': Card, 'Plan': Plan}

#l_monthly
#l_yearly

