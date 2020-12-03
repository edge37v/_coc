from flask import jsonify
from app import create_app, db
from app.models import Entry, Subtopic, Topic

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Entry': Entry, 'Subtopic': Subtopic, 'Topic': Topic}