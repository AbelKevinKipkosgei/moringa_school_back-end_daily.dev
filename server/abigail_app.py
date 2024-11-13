from flask import jsonify, make_response, render_template, request
from flask_restful import Resource
from config import app, api, db, jwt_required, get_jwt_identity
from models import (
    User,
    Post,
    Comment,
    Subscription,
    Like,
    Notification,
    Category,
)


# Home Resource
class HomeResource(Resource):
    def get(self):
        return make_response(jsonify({"message": "Welcome to the API"}), 200)


# checks if the user is a user or a techwriter
def has_access(role):
    return role in ["user", "techwriter"]


class CreatePost(Resource):
    @jwt_required()
    def post(self):
        # Returns user ID or similar identity
        user_identity = get_jwt_identity()
        user = User.query.get(user_identity)

        if not has_access(user.role):
            return {"message": "Unauthorized access"}, 403

        data = request.get_json()
        title = data.get("title")
        body = data.get("body")

        if not title or not body:
            return {"message": "Title and body are required"}, 400

        new_post = Post(title=title, body=body, user_id=user.id)
        db.session.add(new_post)
        db.session.commit()

        return {"message": "Post created successfully", "post": new_post.id}, 201


class ReadPost(Resource):
    @jwt_required()
    def get(self, post_id):
        # Returns user ID or similar identity
        user_identity = get_jwt_identity()
        user = User.query.get(user_identity)

        if not has_access(user.role):
            return {"message": "Unauthorized access"}, 403

        post = Post.query.get(post_id)
        if not post:
            return {"message": "Post not found"}, 404

        return {
            "id": post.id,
            "title": post.title,
            "body": post.body,
            "user_id": post.user_id,
        }, 200


class LikePost(Resource):
    @jwt_required()
    def post(self, post_id):
        # Returns user ID or similar identity
        user_identity = get_jwt_identity()
        user = User.query.get(user_identity)

        if not has_access(user.role):
            return {"message": "Unauthorized access"}, 403

        post = Post.query.get(post_id)
        if not post:
            return {"message": "Post not found"}, 404

        post.likes_count += 1
        db.session.commit()

        return {"message": "Post liked", "likes_count": post.likes_count}, 200


class CommentPost(Resource):
    @jwt_required()
    def post(self, post_id):
        # Returns user ID or similar identity
        user_identity = get_jwt_identity()
        user = User.query.get(user_identity)

        if not has_access(user.role):
            return {"message": "Unauthorized access"}, 403

        post = Post.query.get(post_id)
        if not post:
            return {"message": "Post not found"}, 404

        data = request.get_json()
        comment_body = data.get("comment")

        if not comment_body:
            return {"message": "Comment body is required"}, 400

        # example
        new_comment = Comment(body=comment_body, user_id=user.id, post_id=post.id)
        db.session.add(new_comment)
        db.session.commit()

        return {
            "message": "Comment added successfully",
            "comment_id": new_comment.id,
        }, 201


# Registering routes
api.add_resource(HomeResource, "/api")
api.add_resource(CreatePost, "/api/posts")
api.add_resource(ReadPost, "/api/posts/<int:post_id>")
api.add_resource(LikePost, "/api/posts/<int:post_id>/like")
api.add_resource(CommentPost, "/api/posts/<int:post_id>/comment")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
