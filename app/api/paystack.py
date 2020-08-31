import os
from flask import request, jsonify, current_app
from app import db
from app.api import bp
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

@bp.route('/paystack/create_card/<int:id>', methods=['POST'])
def create_card(id):
    data = request
    user = User.query.get(id)
    card = Card.query.filter_by(signature=data[3]['authorization']['signature']).first()
    if not card:
        card = Card()
        card.user_id = user.id
    card.from_dict()
    db.session.add(card)
    db.session.commit()
    return jsonify({'status': True})

@bp.route('/paystack/create_customer/<email>', methods=['POST'])
def create_customer(email):
    user = User.query.filter_by(email=email).first()
    customer = Customer(authorization_key=sk)
    response = customer.create(user.email, user.first_name, user.last_name, user.phone)
    user.ps_id = response[3]['id']
    db.session.commit()
    return jsonify(response)

@bp.route('/paystack/get_customer/<email>', methods=['GET'])
def get_customer(email):
    customer = Customer(authorization_key=sk)
    user = User.query.filter_by(email=email).first()
    response = customer.getone(user.ps_id)
    return jsonify(response)

@bp.route('/paystack/get_customers', methods=['GET'])
def get_customers():
    customer = Customer(authorization_key=sk)
    response = customer.getall()
    return jsonify(response)

@bp.route('/paystack/verify_transaction/<ref>', methods=['GET'])
def verify_transaction(ref):
    transaction = Transaction(authorization_key=sk)
    response = transaction.verify(ref)
    return response

@bp.route('/paystack/charge_user', methods=['POST'])
def charge_user():
    data = request.get_json()
    amount = data['amount']
    plan = data['plan']
    id = data['id']
    authorization_code = data['authorization_code']
    card = Card.query.join(User, (User.id == Card.user_id)).filter(Card.authorization_code == authorization_code).first()
    user = User.query.get(id)
    transaction = Transaction(authorization_key=sk)
    if not user.ps_id:
        customer = Customer(authorization_key=sk)
        got = customer.create(user.email, user.first_name, user.last_name, user.phone)
        user.ps_id = got[3]['id']
        db.session.commit()
    response = transaction.charge(user.email, card.authorization_code, amount)
    user.plans.append(plan)
    return jsonify(response)

