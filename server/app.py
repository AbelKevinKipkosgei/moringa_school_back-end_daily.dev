from flask import jsonify, make_response, render_template, request
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    current_user,
    login_required,
)
from flask_restful import Resource
from config import app, api, db
from user_model import User
from post_model import Post
from notification_model import Notification
from comment_model import Comment
from like_model import Like
from subscription_model import Subscription
from category_model import Category

# Home Resource
class HomeResource(Resource):
    def get(self):
        return make_response(jsonify({"message": "Welcome to the API"}), 200)


api.add_resource(HomeResource, "/api")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
