from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SubmitField, TextAreaField, SelectField, SelectMultipleField, FileField
from wtforms.validators import DataRequired, Email, Length, URL, ValidationError
from flask_login import current_user
from .models import User

class AddServiceForm(FlaskForm):
	name = StringField('Service name')
	submit = SubmitField('Add')

class EditServiceForm(FlaskForm):
	name = StringField('Service name')
	submit = SubmitField('Save Changes')

class CreateStoreForm(FlaskForm):
	name = StringField('Store name')
	submit = SubmitField('Create')

class EditStoreForm(FlaskForm):
	name = StringField('Store Name')
	submit = StringField('Save Changes')

class AddProductForm(FlaskForm):
	name = StringField('Item name')
	info = TextAreaField('Info')
	store = SelectMultipleField(u'Store', coerce=int)
	produced_by = SelectMultipleField(u'Produced by', coerce=int)
	submit = SubmitField('Add')

class EditProductForm(FlaskForm):
	name = StringField('Item name')
	produced_by = SelectField(u'Produced by')
	submit = SubmitField('Save Changes')