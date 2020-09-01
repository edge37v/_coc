import os
from flask import request, jsonify, current_app
from app import db
from app.api import bp
from app.api.errors import error_response, bad_request
from app.models import User, Card, Plan
from app.api.auth import token_auth
from pypaystack import Transaction, Customer, Plan
import json

status = os.environ.get('STATUS')
ptk = 'sk_test_8e071e9e820c7e0a10040d3f1124ba59d9b3c2d2'
psk = 'sk_live_2567f775551d1f3e53665e529791d2e68072d213'
if status:
    sk = psk
else:
    sk = ptk

@bp.route('/paystack/init/<ref>', methods=['GET', 'POST'])
def init(ref):
    a = request.get_json()
    q = Transaction(authorization_key=sk)
    r = q.verify_transaction(ref)
    c = r[3][customer]
    p = Plan.query.get(a[plan])
    if r[3][status] == 'success':
        u = User.query.filter_by(email).first()
        if not user:
            user = User(email=c[email], password=a[password], \
                    first_name=c[first_name], last_name=c[last_name])
            user.subscribe(p)
            user.customer_code = r[3][customer_code]
        card = Card.query.filter_by(r[3][authorization]\
            [authorization_code])
        if not card:
            card = Card()
            card.authorization_code = r[3][authorization][authorization_code]
        card.user_id(user.id)
        db.session.add(user)
        db.session.add(card)
        db.session.commit()
    else:
        return {'status': 'failed'}
    x = user.to_dict()
    return jsonify({x})

@bp.route('/paystack/get_customer/<email>', methods=['GET'])
def get_customer(email):
    customer = Customer()
    user = User.query.filter_by(email=email).first()
    response = customer.getone(user.ps_id)
    return jsonify(response)

@bp.route('/paystack/verify_transaction/<ref>', methods=['GET'])
def verify_transaction(ref):
    transaction = Transaction()
    response = transaction.verify(ref)
    return response

@bp.route('/paystack/charge_user', methods=['POST'])
def charge_user():
    data = request.get_json()
    plan = data['plan']
    user = data['user']
    plan = Plan.query.get(plan)
    user = User.query.get(user)
    transaction = Transaction()
    response = transaction.charge(user.email, user.customer_code, plan.amount)
    if response[3][status] == 'failed':
        return {'status': 'failed'}
    user.plans.append(plan)
    return {'status': 'success'}

