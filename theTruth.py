from flask import jsonify
from app import create_app, db
from app.models import Entry, Subcategory, Category

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'Entry': Entry, 'Subcategory': Subcategory, 'Category': Category}