from flask import request, jsonify
from app import db
from app.blog_models import blog_posts, Comment, Blog, BlogPost
from app.api import bp

@bp.route('/get_blogs', methods=['GET'])
def get_blogs():
    page = float(request.args['page'])
    items = Blog.to_collection_dict(Blog.query, page)
    return jsonify(items)

@bp.route('/get_blog', methods=['GET'])
def get_blog():
    id = request.args['id']
    page = float(request.args['page'])
    query = BlogPost.query.join(blog_posts, blog_posts.c.blog_id == id)
    items = BlogPost.to_collection_dict(query, page)
    return jsonify(items)

@bp.route('/add_comment', methods=['POST'])
def add_comment():
    q = request.get_json()
    id = request.args['id']
    body = request.args['body']
    post = BlogPost.query.get(id)
    post.add_comment(body)
    db.session.add(post)
    db.session.commit()