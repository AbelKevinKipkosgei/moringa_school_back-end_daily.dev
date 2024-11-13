from flask import jsonify, make_response, render_template, request
from flask_restful import Resource
from config import app, api, db
from models import User, Post, Comment, Subscription, Like, Notification, Category

# Home Resource
class HomeResource(Resource):
    def get(self):
        return make_response(jsonify({"message": "Welcome to the API"}), 200)


# Admin Route to Get All Users
class AdminAllUsersResource(Resource):
    def get(self):
        users = [user.to_dict() for user in User.query.all()]
        return make_response(jsonify(users), 200)


# Admin Route to Reactivate a Deactivated User
# class AdminReactivateUserResource(Resource):
#     def put(self):
#         data = request.get_json()
#         user_id = data.get('user_id')
#         user = User.query.get(user_id)
        
#         if not user:
#             return make_response(jsonify({"message": "User not found"}), 404)
        
#         if user.active:
#             return make_response(jsonify({"message": "User is already active"}), 400)
        
#         user.active = True
#         db.session.commit()
        
#         return make_response(jsonify({"message": "User reactivated successfully"}), 200)


# # Admin Route to Deactivate a User
# class AdminDeactivateUserResource(Resource):
#     def put(self):
#         data = request.get_json()
#         user_id = data.get('user_id')
#         user = User.query.get(user_id)
        
#         if not user:
#             return make_response(jsonify({"message": "User not found"}), 404)
        
#         user.active = False
#         db.session.commit()
        
#         return make_response(jsonify({"message": "User deactivated successfully"}), 200)


# # Admin Route to Delete a Post
# class AdminDeletePostResource(Resource):
#     def delete(self):
#         data = request.get_json()
#         post_id = data.get('post_id')
#         post = Post.query.get(post_id)
        
#         if not post:
#             return make_response(jsonify({"message": "Post not found"}), 404)
        
#         db.session.delete(post)
#         db.session.commit()
        
#         return make_response(jsonify({"message": "Post deleted successfully"}), 200)


# Additional routes 

# Adding resources to the API
api.add_resource(HomeResource, "/api")
api.add_resource(AdminAllUsersResource, "/api/admin/users")
# api.add_resource(AdminReactivateUserResource, "/api/admin/reactivateuser")
# api.add_resource(AdminDeactivateUserResource, "/api/admin/deactivateuser")
# api.add_resource(AdminDeletePostResource, "/api/admin/deletepost")

if __name__ == "__main__":
    app.run(port=5555, debug=True)