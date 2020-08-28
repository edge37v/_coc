import os
from app.email import send_user_email
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import (Blueprint, flash, redirect, render_template, request, url_for)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user, login_user, logout_user, login_required
from . import login, create_app, db
from app.models import User
from app.auth_forms import RegistrationForm, DetailForm, EditUserForm, LoginForm

bp = Blueprint('auth', __name__, url_prefix='/auth')

@login.user_loader
def load_user(id):
        return User.query.get(int(id))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('pages.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        #user.followed.append(user)
        db.session.add(user)
        db.session.commit()
        send_user_email(user)
        flash('A user confirmation email has been sent to you')
        return redirect(url_for('auth.register'))
    return render_template('auth/signup.htm', title='Sign up', form=form)

@bp.route('/confirm_account/<token>')
def confirm_account(token):
        user = User.check_utoken(token)
        if not user:
                return redirect(url_for('pages.index'))
        user.confirmed = True
        login_user(user)
        return redirect(url_for('pages.user', email=user.email))

@bp.route('/detail', methods=['GET', 'POST'])
@login_required
def detail():
        form = DetailForm()
        if form.validate_on_submit():
                current_user.name = form.name.data
                current_user.website = form.website.data
                current_user.tel_number = form.tel_number.data
                current_user.about = form.about.data
                db.session.commit()
                return redirect(url_for('pages.index'))
        return render_template('auth/detail.htm', form=form)

@bp.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
        form = EditUserForm()
        if form.validate_on_submit():
                #f = form.logo.data
                #filename = secure_filename(f.filename)
                #f.save(url_for('static', filename='logos/filename'))
                #user = User.query.filter_by(email=current_user.email).first()
                #if not user.check_password(form.old_password.data):
                #        flash('Incorrect password')
                #        return redirect(url_for('auth.edit_user'))
                current_user.name = form.name.data
                current_user.website = form.website.data
                #current_user.business = Business.query.get(form.business.data)
                current_user.about = form.about.data
                current_user.tel_number = form.tel_number.data
                current_user.email = form.email.data
                #current_user.password = form.new_password.data
                db.session.add(current_user._get_current_object())
                db.session.commit()
                return redirect(url_for('pages.user', email=current_user.email))
        form.name.data = current_user.name
        form.website.data = current_user.website
        form.about.data = current_user.about
        form.email.data = current_user.email
        form.tel_number.data = current_user.tel_number
        return render_template('auth/edit_user.htm', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
        if current_user.is_authenticated:
                return redirect(url_for('index.index'))
        form = LoginForm()
        if form.validate_on_submit():
                user = User.query.filter_by(email=form.email.data).first()
                if not user.check_password(form.password.data):
                        flash('Incorrect password')
                        return redirect(url_for('auth.login'))
                if not user.confirmed:
                        flash('Account is not yet confirmed')
                        return redirect(url_for('auth.login'))
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                        next_page = url_for('pages.index')
                return redirect(next_page)
        return render_template('auth/login.htm', title='Log In', form=form)

@bp.route('/logout')
def logout():
        logout_user()
        return redirect(url_for('pages.index'))
