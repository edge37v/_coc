import os
from flask import request, jsonify, current_app
from flask_cors import cross_origin
from app import db
from app.api import bp
from app.api.errors import error_response, bad_request
from app.models import User, Card, Plan
from app.api.auth import token_auth
from pypaystack import Transaction, Customer
import json

@bp.route('paystack/p_test', methods=['POST'])
def p_test():
    a = request.get_json()
    iSay = a['iSay']
    return jsonify({'you_said': iSay})

@bp.route('paystack/init', methods=['POST'])
def init():
    a = request.get_json()
    reference = a['reference']
    q = Transaction()
    r = q.verify(reference)
    if r is not None:
        if r[3]['status'] == 'success':
            #plan = a['plan']
            #p = Plan.query.filter_by(name=plan).first()
            c = r[3]['customer']
            email = c['email']
            user = User.query.filter_by(email=email).first()
            if user:
                return bad_request('User already registered')
            else:
                user = User(email=c['email'], \
                        first_name=c['first_name'], last_name=c['last_name'])
                password = a['password']
                user.set_password(password)
                user.l_access = True
                user.customer_code = c['customer_code']
            card = Card.query.filter_by(authorization_code = r[3]['authorization']['authorization_code'])
            if not card:
                card = Card()
                card.authorization_code = r[3]['authorization']['authorization_code']
            #card.user_id(user.id)
            db.session.add(user)
            #db.session.add(card)
            db.session.commit()
            x = user.to_dict()
        else:
            return {'status': 'failed'}
    else:
        return {'status': 'failed'}
    return jsonify(x)

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
    if response[3]['status'] == 'failed':
        return {'status': 'failed'}
    user.plans.append(plan)
    return {'status': 'success'}

