import boto3
import Transaction from pypaystack
from flask import jsonify, request
from app.api import bp
from app.models import User
from app.ad_models import user_ads, Ad
from app import db
from flask_jwt_extended import jwt_required

s3 = boto3.resource('s3')

@bp.route('/ads/listen', methods=['POST'])
def listen():
    a = request.get_json()
    if a['event'] == 'subscription_create':
        data = a['data']
        metadata = data['customer']['metadata']
        service = metadata['service']
        if service == 'ads':
            return redirect(url_for('ads.listen', )

@bp.route('/get_ad', methods=['GET'])
def get_ad():
    return jsonify({'url': Ad.get()})

@bp.route('/get_ads', methods=['GET'])
@jwt_required
def get_ads():
    id = request.args['id']
    page = request.args['page']
    query = Ad.query.join(user_ads, user_ads.c.user_id == id)
    return jsonify(Ad.to_collection_dict(query, page))

@bp.route('/add_ad', methods=['GET'])
@jwt_required
def add_ad():
    q = request.get_json()
    id = q['id']
    user = User.query.get(id)
    ad = Ad()
    #user.ads.append(ad)
    #db.session.commit()

@bp.route('/edit_ad', methods=['PUT'])
@jwt_required
def edit_ad():
    pass

@bp.route('/delete_ad', methods='DELETE')
@jwt_required
def delete_ad():
    q = request.get_json()
    id = q['id']
    ad = Ad.query.get(id)
    db.session.delete(ad)
    db.session.commit()

