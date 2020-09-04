from app import create_app, db
from app.models import User, Card, LPlan

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Card': Card, 'LPlan': LPlan}

#l_monthly
#l_yearly

