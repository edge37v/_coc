import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import (Blueprint, flash, redirect, render_template, request, url_for)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from . import login, create_app, db
from app.models import User

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/create_store', methods=['GET', 'POST'])
@login_required
def create_store():
	form: CreateStoreForm = CreateStoreForm()
	if form.validate_on_submit():
		store = Store(name=form.name.data, user_id=current_user.id)
		db.session.add(store)
		db.session.commit()
		return redirect(url_for('pages.store', id=store.id))
	return render_template('store/create_store.htm', form=form)

@bp.route('/store/<int:id>')
@login_required
def store(id):
	store = Store.query.get_or_404(id)
	user = Store.user
	return render_template('pages/store.htm', store=store, user=user)

@bp.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
	form = AddProductForm()
	form.produced_by.choices = [(p.id, p.name) for p in Producer.query.order_by('name')]
	if form.validate_on_submit():
		product = Product(name=form.name.data, info=form.info.data, produced_by=form.produced_by.data)
		db.session.add(product)
		db.session.commit()
		return redirect(url_for('pages.product', id=product.id))
	return render_template('user/add_product.htm', form=form)

@bp.route('/product/delete_product/<int:id>')
@login_required
def delete_product():
	product = Product.query.get(id).first_or_404


@bp.route('/store/delete_store/<int:id>')
@login_required
def delete_store():
	store = Store.query.get_or_404(id)
	db.session.pop(store)
	db.session.commit()
	return redirect(url_for('pages.store', id=store.id))

@bp.route('/add_service', methods=['GET', 'POST'])
@login_required
def add_service():
	form = AddServiceForm
	if form.validate_on_submit():
		service = Service(name=form.name.data, user=current_user._get_current_object())
		db.session.add(service)
		db.session.commit()
		return url_for('user.service', service_id=service.id)
	return render_template('user/add_service.htm', form=form)

@bp.route('/user_services/<int:user_id>')
@login_required
def user_services():
	user = User.query.get_or_404(id)
	services = Ser

@bp.route('/delete_service/<int:service_id>')
@login_required
def delete_service():
	service = Service.query.get(service_id)
	db.session.pop(service)
	return redirect(url_for('user.services', user_id=service.user_id))

