from app.forum_models import Forum, Post, Reply

@bp.route('/forums/get_forums')
def get_forums():
    forums = Forum.query.all()
    return {'forums': [forum.to_dict() for forum in Forum.query.items]}