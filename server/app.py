from functools import wraps
import cloudinary
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, get_jwt_identity, jwt_required
from flask_restful import Resource, reqparse
from config import app, api, db, jwt
from models import Category, Comment, Like, Notification, Subscription, User, Post, Wishlist

# Blacklist check for both access and refresh tokens
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in app.config['BLACKLIST']

# Home Resource
class HomeResource(Resource):
    def get(self):
        return {"message": "Welcome to the API"}, 200

# Signup Resource
class SignupResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='Username is required')
        parser.add_argument('email', required=True, help='Email is required')
        parser.add_argument('password', required=True, help='Password is required')
        data = parser.parse_args()

        # Check if user exists by email
        if User.query.filter_by(email=data['email']).first():
            return {"message": "User with this email already exists"}, 400
        
        # Create a new user
        new_user = User(username=data['username'], email=data['email'])

        # Hashing handled by the password setter
        new_user.password = data['password']
        db.session.add(new_user)
        db.session.commit()

        return {"message": "User created successfully"}, 201
    
# Login Resource
class LoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help='Email is required')
        parser.add_argument('password', required=True, help='Password is required')
        data = parser.parse_args()

        # Find user by email
        user = User.query.filter_by(email=data['email']).first()

        # Authenticate user
        if not user or not user.authenticate(data['password']):
            return {"message": "Invalid credentials"}, 401
        
        # Create JWT token
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200

# Refresh Token Resource
class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return {'access_token': access_token }, 200
    
# Logout Resource
class LogoutResource(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        app.config['BLACKLIST'].add(jti)
        return {"message": "Logged out successfully"}, 200
    
# Admin Route to Get All Users
class AdminAllUsersResource(Resource):
    @jwt_required()
    def get(self):
        users = [user.to_dict() for user in User.query.all()]
        return {"users": users}, 200


# Admin Route to Reactivate a Deactivated User
class AdminReactivateUserResource(Resource):
    @jwt_required()
    def put(self, user_id):
        # Get the identity (User ID) from th JWT token
        current_user_id = get_jwt_identity()

        # Fetch the current user from the database
        current_user = User.query.get(current_user_id)

        # Check if the current user is an admin
        if current_user.role != 'admin':
            return {"message": "Unauthorized access"}, 403
        
        # Fetch the user to be reactivated
        user = User.query.get(user_id)

        if not user:
            return {"message": "User not found"}, 404
        
        if user.activated:
            return {"message": "User is already active"}, 404
        
        # Reactivate the user
        user.activated = True
        db.session.commit()

        return {"message": "User reactivated successfully"}, 200
    
class AdminDeactivateUserResource(Resource):
    @jwt_required()
    def put(self, user_id):
        # Get the identity (User ID) from the JWT token
        current_user_id = get_jwt_identity()

        # Fetch the current user from the database
        current_user = User.query.get(current_user_id)

        # Check if current user is an admin
        if current_user.role != 'admin':
            return {"message": "Unauthorized access"}, 403
        
        # Fetch the user to be deactivated
        user = User.query.get(user_id)
        
        if not user:
            return {"message": "User not found"}, 404
        
        if user.activated == False:
            return {"message": "User is already deactivated"}, 404
        
        # Deactivate the user
        user.activated = False
        db.session.commit()

        return {"message": "User deactivated successfully"}, 200
    
class AdminDeletePostResource(Resource):
    @jwt_required()
    def delete(self, post_id):
        # Get the identity (User ID) from the JWT token
        current_user_id = get_jwt_identity()

        # Fetch the current user from the database
        current_user = User.query.get(current_user_id)

        # Check if current user is an admin
        if current_user.role != 'admin':
            return {"message": "Unauthorized access"}, 403
        
        post = Post.query.get(post_id)

        if not post:
            return {"message": "Post not found"}, 404
        
        # Notify the user before deleting the post
        post.notify_on_delete(current_user)
        
        db.session.delete(post)
        db.session.commit()

        return {"message": "Post deleted successfully"}, 200

# User and Tech writer decorator   
def user_techwriter_role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_identity = get_jwt_identity()
            user = User.query.get(user_identity)
            if not user or user.role not in allowed_roles:
                return {"message": "Unauthorized access"}, 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Create a post        
class CreatePost(Resource):
    @user_techwriter_role_required(['user', 'techwriter'])
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("title", required=True, help="Title is required")
        parser.add_argument("body", required=True, help="Body is required")
        parser.add_argument("category", required=True, help="Category is required")
        parser.add_argument("post_type", required=True, choices=['video', 'audio', 'blog'])
        data = parser.parse_args()

        title=data['title']
        body=data['body']
        category_name=data['category']
        post_type=data['post_type']

        # Check if the category exists
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            return {"message": "Category not found"}, 404
        
        # Handle file upload to cloudinary for thumbnails
        file = request.files.get('thumbnail')
        if not file:
            return {"message": "Thumbnail is required"}, 400
        
        try:
            upload_result = cloudinary.uploader.upload(
                file,
                folder='thumbnails',
                transformation=[
                    {
                        'width': 300,
                        'height': 300,
                        'crop': 'thumb',
                        'radius': 20
                    }
                ]
            )
            thumbnail_url = upload_result['secure_url']
        except Exception as e:
            return {"message": f"Failed to upload thumbnail: {e}"}, 500
    
        # Handle video/audio upload to cloudinary
        media_url = None
        if post_type in ['video', 'audio']:
            media_file = request.files.get('media_file')
            if not media_file:
                return {"message": "Media file is required"}, 400
            try:
                if post_type == 'video':
                    upload_result = cloudinary.uploader.upload(
                        media_file,
                        resource_type='video' if post_type == 'video' else 'raw',
                        folder=f'media/{post_type}'
                    )
                media_url = upload_result['secure_url']
            except Exception as e:
                return {"message": f"Failed to upload media: {e}"}, 500
        
        
        user_identity = get_jwt_identity()
        new_post = Post(
            title=title,
            body=body,
            post_type=post_type,
            thumbnail_url=thumbnail_url,
            media_url=media_url,
            user_id=user_identity,
            category_id=category.id
        )
        db.session.add(new_post)
        db.session.commit()

        # Notify category subscribers about the post
        new_post.notify_category_subscribers()

        return {"message": "Post created successfully", "post": new_post.id}, 201

# Read a post 
class ReadPost(Resource):
    def get(self, post_id):
        post = Post.query.get(post_id)
        if not post:
            return {"message": "Post not found"}, 404
        return {"post": post.to_dict()}, 200

# Like a post
class LikePost(Resource):
    @user_techwriter_role_required(['user', 'techwriter'])
    def post(self, post_id):
        post = Post.query.get(post_id)
        if not post:
            return {"message": "Post not found"}, 404
        
        # Get the current user ID from JWT identity
        user_id = get_jwt_identity()
        liking_user = User.query.get(user_id)

        if not liking_user:
            return {"message": "User not found"}, 404

        # Check whether the user has already like the post
        existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        if existing_like:
            return {"message": "You have already liked this post"}, 400
        
        # Create a new like entry in the database
        new_like = Like(post_id=post_id, user_id=user_id)
        db.session.add(new_like)

        # Increment the likes count on the post
        post.likes_count += 1

        # Notify the post author about the like
        if post.user_id != liking_user.id:
            post.notify_on_like(liking_user)
        
        db.session.commit()

        return {"message": "Post liked", "likes_count": post.likes_count}, 200
    
# Unlike a post
class UnlikePost(Resource):
    @user_techwriter_role_required(['user', 'techwriter'])
    def delete(self, post_id):
        post = Post.query.get(post_id)
        if not post:
            return {"message": "Post not found"}, 404
        
        user_id = get_jwt_identity()
        unliking_user = User.query.get(user_id)

        if not unliking_user:
            return {"message": "User not found"}, 404

        # Check if the like exists
        like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        if not like:
            return {"message": "You have not liked this post"}, 400
        
        # Remove the like entry
        db.session.delete(like)

        # Decrement the likes count on the post
        post.likes_count -= 1

        # Remove the like notification
        post.remove_like_notification(unliking_user)

        db.session.commit()

        return {"message": "Post unliked", "likes_count": post.likes_count}, 200


# Comment on a post
class CommentPost(Resource):
    @user_techwriter_role_required(['user', 'techwriter'])
    def post(self, post_id):
        # Check if the post exists
        post = Post.query.get(post_id)
        if not post:
            return {"message": "Post not found"}, 404
        
        # Get comment data from request
        data = request.get_json()
        comment_body = data.get("comment")
        if not comment_body:
            return {"message": "Comment body is required"}, 400
        
        # Get user identity from the JWT token
        user_identity = get_jwt_identity()
        commenting_user = User.query.get(user_identity)

        # Create the new comment
        new_comment = Comment(body=comment_body, user_id=user_identity, post_id=post.id)
        db.session.add(new_comment)
        db.session.commit()

        # Notify the post author about the new comment
        if post.user_id != commenting_user.id:
            post.notify_on_comment(commenting_user, new_comment)

        return {
            "message": "Comment added successfully",
            "comment_id": new_comment.id,
        }, 200

# Admin and Tech writer decorator
def admin_techwriter_role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_identity = get_jwt_identity()
            user = User.query.get(user_identity)
            if not user or user.role not in allowed_roles:
                return {"message": "Unauthorized access"}, 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Create a new category
class CategoryResource(Resource):
    @admin_techwriter_role_required(['admin', 'techwriter'])
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, help="Category name is required")
        parser.add_argument('description', required=True, help="Category description is required")
        data = parser.parse_args()
        
        name = data.get("name")
        description = data.get("description")
        
        new_category = Category(name=name, description=description)
        db.session.add(new_category)
        db.session.commit()
        
        return {
            "message": "Category created",
            "category": {"name": name, "description": description}
        }, 201

# Approve a post
class ApprovePost(Resource):
    @admin_techwriter_role_required(['admin', 'techwriter'])
    def put(self, post_id):
        post = Post.query.get(post_id)
        if not post:
            return {"error": "Post not found"}, 404

        if post.approved:
            return {"message": "Post is already approved"}, 200

        try:
            post.approved = True
            db.session.commit()
            return {"message": f"Post {post_id} approved"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": "Failed to approve post", "details": str(e)}, 500
        
# Flag a post
class FlagPost(Resource):
    @admin_techwriter_role_required(['admin', 'techwriter'])
    def post(self, post_id):
        # Parse the reason for flagging
        parser = reqparse.RequestParser()
        parser.add_argument('reason', required=True, help="Reason for flagging is required")
        data = parser.parse_args()

        reason = data['reason']

        post = Post.query.get(post_id)
        if not post:
            return {"error": "Post not found"}, 404
        
        if post.flagged:
            return {"message": "Post is already flagged"}, 200
        
        try:
            post.flagged = True
            db.session.commit()

            # Notify the user that their post was flagged
            flagging_user_id = get_jwt_identity()
            flagging_user = User.query.get(flagging_user_id)

            if not flagging_user:
                return {"error": "User not found"}, 404
            
            post.notify_on_flag(flagging_user, reason)

            return {"message": f"Post {post_id} flagged"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": "Failed to flag post", "details": str(e)}

# Unflag a post
class UnflagPost(Resource):
    @admin_techwriter_role_required(['admin', 'techwriter'])
    def post(self, post_id):
        post = Post.query.get(post_id)
        if not post:
            return {"error": "Post not found"}, 404
        
        if not post.flagged:
            return {"message": "Post is not flagged"}, 200
        
        try:
            post.flagged = False
            db.session.commit()

            flagging_user_id = get_jwt_identity()
            flagging_user = User.query.get(flagging_user_id)

            # Remove the notification when the post is unflagged
            post.remove_flag_notification(flagging_user)

            return {"message": f"Post {post_id} is unflagged"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": "Failed to unflag post", "details": str(e)}
        

# Edit a post
class EditPost(Resource):
    @admin_techwriter_role_required(['admin', 'techwriter'])
    def put(self, post_id):
        post = Post.query.get(post_id)
        if not post:
            return {"error": "Post not found"}, 404

        # Allowed fields for update
        allowed_fields = ['title', 'body', 'post_type', 'thumbnail_url', 'media_url', 'likes_count', 'approved']

        data = request.json
        if not isinstance(data, dict):
            return {"error": "Invalid data format. Expected JSON object."}, 400

        updated = False

        for field in allowed_fields:
            if field in data:
                new_value = data[field]
                if getattr(post, field) != new_value:
                    setattr(post, field, new_value)
                    updated = True

        # Commit changes if any updates were made
        if updated:
            post.updated_at = db.func.now()
            db.session.commit()
            message = f"Post {post_id} updated successfully"
        else:
            message = "No changes made to the post"

        return {
            "message": message,
            "post": {
                "id": post.id,
                "title": post.title,
                "body": post.body,
                "post_type": post.post_type,
                "thumbnail_url": post.thumbnail_url,
                "media_url": post.media_url,
                "likes_count": post.likes_count,
                "approved": post.approved,
                "updated_at": post.updated_at.strftime('%Y-%m-%d %H:%M:%S') if post.updated_at else None
            }
        }, 200

    
# User decorator
def user_role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_identity = get_jwt_identity()
            user = User.query.get(user_identity)
            if not user or user.role not in allowed_roles:
                return {"message": "Unauthorized access"}, 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

# User subscription to category
class SubscribeCategory(Resource):
    @user_role_required(['user'])
    def post(self, category_id):
        # Get the currently logged-in user
        user_identity = get_jwt_identity()
        user = User.query.get(user_identity)

        if not user:
            return {"error": "User not found"}, 404

        # Retrieve the category
        category = Category.query.get(category_id)
        if not category:
            return {"error": "Category not found"}, 404

        # Check if the subscription already exists
        existing_subscription = Subscription.query.filter_by(user_id=user.id, category_id=category_id).first()
        if existing_subscription:
            return {
                "message": f"User '{user.username}' is already subscribed to category '{category.name}'"
            }, 200

        # Create a new subscription
        try:
            subscription = Subscription(user_id=user.id, category_id=category_id)
            db.session.add(subscription)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": "Failed to create subscription", "details": str(e)}, 500

        # Return the new subscription details
        return {
            "message": f"User '{user.username}' successfully subscribed to category '{category.name}'",
            "subscription": {
                "id": subscription.id,
                "user": {
                    "id": user.id,
                    "username": user.username
                },
                "category": {
                    "id": category.id,
                    "name": category.name
                }
            }
        }, 201
    

# User unsubscribe from category
class UnsubscribeCategory(Resource):
    @user_role_required(['user'])
    def delete(self, category_id):
        # Get the currently logged-in user
        user_identity = get_jwt_identity()
        user = User.query.get(user_identity)

        if not user:
            return {"error": "User not found"}, 404

        # Retrieve the category
        category = Category.query.get(category_id)
        if not category:
            return {"error": "Category not found"}, 404

        # Check if the subscription exists
        subscription = Subscription.query.filter_by(user_id=user.id, category_id=category_id).first()
        if not subscription:
            return {
                "message": f"User '{user.username}' is not subscribed to category '{category.name}'"
            }, 200

        # Remove the subscription
        try:
            db.session.delete(subscription)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": "Failed to unsubscribe", "details": str(e)}, 500
        
        # Remove any notifications related to the unsubscribed category
        Post.remove_category_subscription_notifications(user, category.name)

        # Return success message
        return {
            "message": f"User '{user.username}' successfully unsubscribed from category '{category.name}'"
        }, 200
    
# Add post to wishlist
class AddToWishlist(Resource):
    @user_role_required(['user'])
    def post(self, post_id):
        # Get the currently logged-in user
        user_identity = get_jwt_identity()
        user = User.query.get(user_identity)

        if not user:
            return {"error": "User not found"}, 404

        # Check if the post exists
        post = Post.query.get(post_id)
        if not post:
            return {"error": "Post not found"}, 404

        # Check if the post is already in the user's wishlist
        existing_wishlist_item = Wishlist.query.filter_by(user_id=user.id, post_id=post_id).first()
        if existing_wishlist_item:
            return {
                "message": f"Post '{post.title}' is already in the wishlist of user '{user.username}'"
            }, 200

        # Add the post to the wishlist
        wishlist_item = Wishlist(user_id=user.id, post_id=post_id)
        db.session.add(wishlist_item)
        db.session.commit()

        # Notify the post author about the wishlist addition
        if post.user_id != user.id:
            post.notify_on_wishlist(user)

        # Return the newly added wishlist item
        return {
            "message": f"Post '{post.title}' added to wishlist for user '{user.username}'",
            "wishlist_item": {
                "id": wishlist_item.id,
                "user": {
                    "id": user.id,
                    "username": user.username
                },
                "post": {
                    "id": post.id,
                    "title": post.title,
                    "thumbnail_url": post.thumbnail_url
                }
            }
        }, 201

# Remove post from wishlist
class RemoveFromWishlist(Resource):
    @user_role_required(['user'])
    def delete(self, post_id):
        # Get the currently logged-in user
        user_identity = get_jwt_identity()
        user = User.query.get(user_identity)

        if not user:
            return {"error": "User not found"}, 404

        # Check if the post exists
        post = Post.query.get(post_id)
        if not post:
            return {"error": "Post not found"}, 404

        # Check if the post is in the user's wishlist
        wishlist_item = Wishlist.query.filter_by(user_id=user.id, post_id=post_id).first()
        if not wishlist_item:
            return {
                "message": f"Post '{post.title}' is not in the wishlist of user '{user.username}'"
            }, 404

        # Remove the post from the wishlist
        db.session.delete(wishlist_item)
        db.session.commit()

        # Notify the post author about the wishlist removal
        if post.user_id != user.id:
            post.remove_wishlist_notification(user)

        # Return a success message
        return {
            "message": f"Post '{post.title}' removed from wishlist for user '{user.username}'"
        }, 200

# Fetch paginated user notifications
class GetNotifications(Resource):
    @user_role_required(['user'])
    def get(self):
        # Get the currently logged-in user
        user_identity = get_jwt_identity()
        user = User.query.get(user_identity)

        if not user:
            return {"error": "User not found"}, 404

        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Paginate notifications
        pagination = Notification.query.filter_by(user_id=user.id).order_by(
            Notification.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        notifications = pagination.items

        # Return paginated notifications
        return {
            "user": {
                "id": user.id,
                "username": user.username
            },
            "notifications": [
                {
                    "id": notification.id,
                    "message": notification.message,
                    "created_at": notification.created_at.isoformat()
                } for notification in notifications
            ],
            "pagination": {
                "current_page": pagination.page,
                "total_pages": pagination.pages,
                "total_notifications": pagination.total
            }
        }, 200


# Resource routes
api.add_resource(HomeResource, '/api', endpoint='home')
api.add_resource(SignupResource, '/api/signup', endpoint='signup')
api.add_resource(LoginResource, '/api/login', endpoint='login')
api.add_resource(RefreshResource, '/api/refresh', endpoint='refresh')
api.add_resource(LogoutResource, '/api/logout', endpoint='logout')
api.add_resource(AdminAllUsersResource, '/api/admin/users', endpoint='adminusers')
api.add_resource(AdminReactivateUserResource, '/api/admin/user/reactivate/<int:user_id>', endpoint='reactivateuser')
api.add_resource(AdminDeactivateUserResource, '/api/admin/user/deactivate/<int:user_id>', endpoint='deactivateuser')
api.add_resource(AdminDeletePostResource, '/api/admin/post/delete/<int:post_id>', endpoint='deletepost')
api.add_resource(CreatePost, '/api/posts/createpost', endpoint='createpost')
api.add_resource(ReadPost, '/api/post/read/<int:post_id>', endpoint='read')
api.add_resource(LikePost, '/api/post/like/<int:post_id>', endpoint='like')
api.add_resource(UnlikePost, '/api/post/unlike/<int:post_id>', endpoint='unlike')
api.add_resource(CommentPost, '/api/post/comment/<int:post_id>', endpoint='comment')
api.add_resource(CategoryResource, '/api/categories/createcategory', endpoint='createcategory')
api.add_resource(ApprovePost, '/api/posts/approve/<int:post_id>', endpoint='approve')
api.add_resource(FlagPost, '/api/posts/flag/<int:post_id>', endpoint='flagpost')
api.add_resource(UnflagPost, '/api/posts/unflag/<int:post_id>', endpoint='unflagpost')
api.add_resource(EditPost, '/api/posts/edit/<int:post_id>', endpoint='editpost')
api.add_resource(SubscribeCategory, '/api/category/subscribe/<int:category_id>', endpoint='subscribecategory')
api.add_resource(UnsubscribeCategory, '/api/category/unsubscribe/<int:category_id>', endpoint='unsubscribecategory')
api.add_resource(AddToWishlist, '/api/post/addtowishlist/<int:post_id>', endpoint='addtowishlist')
api.add_resource(RemoveFromWishlist, '/api/post/removefromwishlist/<int:post_id>', endpoint='removefromwishlist')
api.add_resource(GetNotifications, '/api/getnotifications', endpoint='getnotifications')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
