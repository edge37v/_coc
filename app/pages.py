from algoliasearch.search_client import SearchClient
from flask import Flask, Blueprint, url_for, render_template, redirect, request, g
from app.models import User
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from .page_forms import WriteForm, SearchForm
from . import db

bp = Blueprint('pages', __name__)

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        #current_user.last_seen = datetime.utcnow()
        #db.session.commit()
        g.search_form = SearchForm()

@bp.route('/search')
def search():
    form = SearchForm()
    if not form.validate():
        return redirect(url_for('pages.index'))
    users = User.query.whoosh_search(form.q.data)
    return render_template('search.html', users=users)

bp.route('/')
@bp.route('/index')
def index():
    form = SearchForm()
    users = User.query.all()
    return render_template('index.htm', users=users)

@bp.route('/store/<int:id>')
@login_required
def store(id):
	store = Store.query.get(id)
	products = store.products.order_by(Product.timestamp.desc().all())
	return render_template('pages/store.htm', store=store, products=products)

@bp.route('/product/<int:id>')
@login_required
def product(id):
	product = Product.query.get_or_404(id)
	return render_template('pages/product.htm', product=product)

@bp.route('/user/<email>')
def user(email):
    form = RankForm()
    user = User.query.filter_by(email=email).first_or_404()
    return render_template('pages/user.htm', user = user, form=form)

@bp.route('/user/<email>/write', methods=['GET', 'POST'])
def write(email):
        form = WriteForm()
        user = User.query.filter_by(email=email).first_or_404()
        if form.validate_on_submit():
            post = Post(
                title=form.title.data,
                body = form.body.data,
                user_id = user.id)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('pages.index'))
        return render_template('pages/write.htm', form=form, user=user, post=post)
