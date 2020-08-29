from flask import request, jsonify
from app import db
from app.api import bp
from app.models import User, Card, MPlan as Plan
from app.api.auth import token_auth
from pypaystack import Transaction, Customer, Plan
import json

sk = "sk_test_8e071e9e820c7e0a10040d3f1124ba59d9b3c2d2"

@bp.route('/paystack/create_card', methods=['POST'])
def create_card():
    data = request
    card = Card.query.filter_by(signature=data[3]['authorization']['signature']).first()
    if not card:
        card = Card()
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

@bp.route('/paystack/charge_user_monthly', methods=['POST'])
def charge_user_monthly():
    data = request.get_json()
    ps_email = data['ps_email']
    authorization_code = data['authorization_code']
    card = Card.query.join(User, (User.id == Card.user_id)).filter(Card.authorization_code == authorization_code).first()
    user = User.query.filter_by(ps_email=ps_email).first()
    transaction = Transaction(authorization_key=sk)
    if not user.ps_id:
        customer = Customer(authorization_key=sk)
        response = customer.create(user.email, user.first_name, user.last_name, user.phone)
        user.ps_id = response[3]['id']
        db.session.commit()
    response = transaction.charge(user.email, card.authorization_code, 100000)
    return jsonify(response)

@bp.route('/create_plan', methods=['POST'])
def create_plan():
    data = request.get_json() or {}
    mplan = MPlan()
    mplan.from_dict(data)
    db.session.add(mplan)
    db.session.commit()
    plan = Plan(authorization_key=sk)
    response = plan.create(db_plan.name, db_plan.amount, db_plan.period)
    #db_plan.ps_id = response.id
    return jsonify(response)

