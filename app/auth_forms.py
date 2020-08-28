from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, URL, ValidationError
from flask_login import current_user
from .models import User

class RegistrationForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Sorry, that email is already registered")

class DetailForm(FlaskForm):
    name = StringField("Your business's name", validators=[Length(max=37)])
    #business = SelectField("Your business's category", coerce=int)
    website = StringField('Website')
    about = StringField('About your business', validators=[Length(max=123)])
    tel_number = StringField('Contact Number')
    email = StringField('Email',)
    submit = SubmitField('Save')

    def validate_name(self, name):
        user = User.query.filter_by(name=name.data).first()
        if user is not None:
            raise ValidationError("Sorry, some business out there already has that name")

class EditUserForm(FlaskForm):
    logo = FileField('Logo')
    name = StringField("Your business's name", validators=[Length(max=37)])
    website = StringField('Website')
    #business = SelectField("Your business's category", coerce=int)
    about = StringField('About your business', validators=[Length(max=123)])
    tel_number = StringField('Contact Number')
    email = StringField('Email',)
    submit = SubmitField('Save')
    #old_password = PasswordField('Old Password')
    #new_password = PasswordField('New Password')

    def validate_name(self, name):
        user = User.query.filter_by(name=name.data).first()
        if user is not None and user != current_user:
            raise ValidationError("Sorry, some business out there already has that name")

class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember me')
    submit = SubmitField('Log in')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("An account with that email don't exist")
        

