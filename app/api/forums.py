from flask import request, jsonify
from app import db
from app.api import bp
from app.forum_models import forum_posts, Forum, Forumpost

@bp.route('/forums/write', methods=['POST'])
def write():
    q = request.get_json()
    id = q['id']
    body = q['body']
    reply_to_id = q['reply_to_id'] or None
    forum = Forum.query.get(id)
    reply_to = Forumpost.query.get(reply_to_id)
    post = Forumpost(body, reply_to)
    forum.append(post)
    db.session.commit()

@bp.route('/get_forums', methods=['GET'])
def get_forums():
    page = request.args['page']
    query = Forum.query.all()
    items = Forum.to_collection_dict(query, page)
    return jsonify(items)

@bp.route('/get_forum', methods=['GET'])
def get_forum():
    id = request.args['id']
    page = request.args['page']
    query = Forumpost.query.join(forum_posts, forum_posts.c.forum_id == id)
    items = Forumpost.to_collection_dict(query, page)
    return jsonify(items)