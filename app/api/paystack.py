import os
from flask import request, jsonify, current_app
from flask_cors import cross_origin
from app import db
from app.api import bp
basedir = os.path.abspath(os.path.dirname(__file__))
from app.api.errors import response, bad_request
from app.models import User, Card, Year, Module
from app.api.auth import token_auth
from pypaystack import Transaction, Customer
import json

@bp.before_request
def log_request():
    current_app.logger.debug('Request: %s', request)

@bp.route('paystack/initialize', methods=['POST'])
def initialize():
    q = request.get_json()
    email = q['email']
    amount = q['amount']
    metadata = q['metadata']
    t = Transaction()
    url = t.initialize(email=email, amount=amount, metadata=metadata)
    if not url:
        return response(500, 'Could not initialize the transaction')
    return jsonify({'url':url})

@bp.route('paystack/listen', methods=['POST'])
def listen():
    a = request.get_json()
    if a['event'] == 'subscription_create':
        data = a['data']
        metadata = data['customer']['metadata']
        year = metadata['year']
        module = metadata['module']
        email = metadata['email']
        password = metadata['password']
        user = User(email=email, password=password)
        user.subscribe(year, module)
        user.confirmed=true
        db.session.commit()

@bp.route('paystack/init', methods=['POST'])
def init():
    a = request.get_json()
    email = a['email'] 
    t=Transaction()
    user=User.query.filter_by(email=email).first()
    if user:
        return bad_request('User already registered')
    r = t.initialize(email=email, amount=amount)
    if not r:
        return bad_request("something's wrong")
    
    auth_url = r[3]['authorization_url']
    return jsonify({'url': auth_url})

@bp.route('paystack/card', methods=['POST'])
def card():
    a = request.get_json()
    reference = a['reference']
    r = Transaction().verify(reference)
    if r:
        if r[3]['status'] == 'success':
            #year = a['year']
            #module = a['module']
            password = a['password']
            c = r[3]['customer']
            email = c['email']
            year = Year.query.filter_by(name=year).first()
            module = Module.query.filter_by(name=module).first()
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(email=c['email'], first_name=c['first_name'], last_name=c['last_name'])
                user.confirmed = True
                db.session.add(user)
            #user.subscribe(year, module)
            user.set_password(password)
            user.customer_code = c['customer_code']
            card_auth = r[3]['authorization']['authorization_code']
            card = Card.query.filter_by(authorization_code = card_auth).first()
            if not card:
                card = Card()
                card.authorization_code = card_auth
            db.session.add(card)
            db.session.commit()
            x = user.to_dict()
        else:
            return {'status': 'failed'}
    else:
        return response(500, "Sorry, we've got an error, it's personal")
    return jsonify(x)