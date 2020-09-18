from app.forum_models import Forum, Post, Reply

@bp.route('/forums/get_forums')
def get_forums():
    forums = Forum.query.all()
    return jsonify({'forums': [forum.to_dict() for forum in Forum.query.items]})

@bp.route('/forums/get_forum')
def get_forum():
    id = request.args[id]
    forum = Forum.query.get(id)
    return jsonify(forum.to_dict())