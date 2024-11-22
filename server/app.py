import datetime
from functools import wraps
from sqlalchemy import desc
from werkzeug.exceptions import HTTPException
import cloudinary
from sqlalchemy.orm.exc import NoResultFound
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request
from werkzeug.utils import secure_filename
from flask_restful import Resource, reqparse
from config import app, api, db, jwt, redis_client
from models import Category, Comment, Like, Notification, Subscription, User, Post, Wishlist
import datetime
import json

# Blacklist check for both access and refresh tokens
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return redis_client.get(jti) is not None

# Custom JSONEncoder to handle datetime serialization
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()  # Handle datetime serialization globally
        return super().default(obj)
    
app.json_encoder = CustomJSONEncoder

# If you're using Flask-RESTful's `output_json`, ensure it's using the custom encoder
api.representations['application/json'] = lambda data, code, headers=None: (
    app.response_class(
        response=json.dumps(data, default=str),  # Use the custom encoder here
        status=code,
        mimetype='application/json'
    )
)

# Home Resource
class HomeResource(Resource):
    def get(self):
        return {"message": "Welcome to the API"}, 200

# Signup Resource
class SignupResource(Resource):
    def post(self):
        # Parse form fields
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        bio = request.form.get('bio')
        profile_pic = request.files.get('profile_pic_url')
        
        # Validate required fields
        if not all([username, email, password, bio]):
            return {"message": "All fields are required"}, 400
        
        # Validate profile pic
        if 'profile_pic_url' not in request.files:
            return {"message": "Profile picture is missing"}, 400

        # Check if user exists by email
        if User.query.filter_by(email=email).first():
            return {"message": "User with this email already exists"}, 400

        # Check if username exists
        if User.query.filter_by(username=username).first():
            return {"message": "Username already exists"}, 400
        
        # Handle the image upload to Cloudinary if a file is provided
        image_url = None
        if profile_pic:
            # Ensure the file is safe to use
            filename = secure_filename(profile_pic.filename)

            # Upload the image to Cloudinary
            upload_result = cloudinary.uploader.upload(
                profile_pic,
                public_id=username,  # Use username as the public ID
                transformation=[
                    {
                        'crop': 'thumb', # Crop the image to a square
                        'gravity': 'face', # Focus on the face if present
                        'width': 200, # Width of the image
                        'height': 200, # Height of the image
                        'radius': 'max', # Apply circular transformation
                    }
                ]
            )

            # Get the URL of the uploaded image
            image_url = upload_result.get('secure_url')

        # Create a new user with the provided details
        new_user = User(
            username=username,
            email=email,
            bio=bio,
            profile_pic_url=image_url
        )

        # Hashing handled by the password setter
        new_user.password = password

        # Add new user to session and commit
        db.session.add(new_user)
        db.session.commit()

        return {"message": "User created successfully"}, 201
    
# Login Resource
class LoginResource(Resource):
    def post(self):
        try:
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
            access_token = create_access_token(identity={"id": user.id, "role": user.role})
            refresh_token = create_refresh_token(identity={"id": user.id, "role": user.role})

            # Return the tokens
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'role': user.role,
                'userId': user.id,
                'profilePicture': user.profile_pic_url
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500

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
        # Get the jti (JWT ID) from the current JWT
        jti = get_jwt()['jti']

        # Check if the token is already blacklisted
        if redis_client.get(jti):
            return {"message": "Token already logged out"}, 400

        # Add the JWT ID to the blacklist in Redis
        redis_client.setex(jti, int(app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()), 'true')

        return {"message": "Logged out successfully"}, 200
    
# Admin Route to Get All Users
class AdminAllUsersResource(Resource):
    @jwt_required()
    def get(self):
        users = [user.to_dict() for user in User.query.all()]
        return {"users": users}, 200


class AdminReactivateUserResource(Resource):
    @jwt_required()
    def put(self, user_id):
        # Get the identity (User ID) from the JWT token
        current_user_info = get_jwt_identity()
        current_user_id = current_user_info.get('id')

        if not current_user_id:
            return {"message": "User ID is missing or invalid"}, 400

        try:
            current_user_id = int(current_user_id)  # Ensure the ID is an integer
        except ValueError:
            return {"message": "Invalid user ID format"}, 400

        # Fetch current user
        current_user = db.session.get(User, current_user_id)
        if not current_user:
            return {"message": "Current user not found"}, 404

        # Ensure current user is an admin
        if current_user.role != "admin":
            return {"message": "Unauthorized access"}, 403

        # Fetch the user to reactivate
        user_to_reactivate = db.session.get(User, user_id)
        if not user_to_reactivate:
            return {"message": "User not found"}, 404

        # Check if the user is already active
        if user_to_reactivate.activated:
            return {"message": "User is already active"}, 400

        # Reactivate the user
        user_to_reactivate.activated = True
        db.session.commit()

        return {"message": f"User {user_to_reactivate} reactivated successfully"}, 200
    
class AdminDeactivateUserResource(Resource):
    @jwt_required()
    def put(self, user_id):
        # Get the identity (User ID) from the JWT token
        current_user_info = get_jwt_identity()
        current_user_id = current_user_info.get('id')

        if not current_user_id:
            return {"message": "User ID is missing or invalid"}, 400

        try:
            current_user_id = int(current_user_id)  # Ensure the ID is an integer
        except ValueError:
            return {"message": "Invalid user ID format"}, 400

        # Fetch current user
        current_user = db.session.get(User, current_user_id)
        if not current_user:
            return {"message": "Current user not found"}, 404

        # Ensure current user is an admin
        if current_user.role != "admin":
            return {"message": "Unauthorized access"}, 403

        # Fetch the user to deactivate
        user_to_deactivate = db.session.get(User, user_id)
        if not user_to_deactivate:
            return {"message": "User not found"}, 404

        # Check if the user is already deactivated
        if not user_to_deactivate.activated:
            return {"message": "User is already deactivated"}, 200

        # Deactivate the user
        user_to_deactivate.activated = False
        db.session.commit()

        return {"message": f"User {user_to_deactivate} deactivated successfully"}, 200
class AdminDeletePostResource(Resource):
    @jwt_required()
    def delete(self, post_id):
        # Get the identity (User ID) from the JWT token
        current_user_id = get_jwt_identity()

        current_user_id = current_user_id.get('id') 

        # Fetch the current user from the database
        current_user = User.query.get(current_user_id)

        # Check if current user is an admin
        if current_user.role != 'admin':
            return {"message": "Unauthorized access"}, 403
        
        post = Post.query.get(post_id)
        # Delete associated comments
        Comment.query.filter_by(post_id=post_id).delete()
        db.session.commit()

        if not post:
            return {"message": "Post not found"}, 404
        
        # Notify the user before deleting the post
        post.notify_on_delete(current_user)
        
        db.session.delete(post)
        db.session.commit()

        return {"message": "Post deleted successfully"}, 200

# Fetch all posts
class FetchAllPostsResource(Resource):
    def get(self):
        print("ALL Posts")
        user_id = None
        try:
            # Attempt to verify the JWT in the request
            verify_jwt_in_request(optional=True)
            # Get the identity (User ID) from the JWT token
            user_id = get_jwt_identity()
        except Exception:
            # If the JWT is invalid or missing, skip verification
            pass

        # Fetch all posts and serialize them
        posts = Post.query.join(Category, Category.id == Post.category_id).all()
        serialized_posts = []

        for post in posts:
            serialized_post = post.to_dict()
            # Add category name to the serialized post
            serialized_post['category'] = post.category.name
            # Call the method explicitly with user_id
            serialized_post['is_wishlist_by_user'] = post.is_wishlist_by_user(user_id) if user_id else False
            serialized_posts.append(serialized_post)

        return {"posts": serialized_posts}, 200



# User and Tech writer decorator   
def user_techwriter_role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_info = get_jwt_identity()
            user_id = user_info["id"]
            user = User.query.get(user_id)
            if not user or user.role not in allowed_roles:
                return {"message": "Unauthorized access"}, 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

class CreatePost(Resource):
    @user_techwriter_role_required(['user', 'techwriter'])
    def post(self):
        # Parse incoming data from request.form
        title = request.form.get('title')
        body = request.form.get('body')
        category_name = request.form.get('category')
        post_type = request.form.get('post_type')

        # Validate required fields
        if not title or not body or not category_name or not post_type:
            return {"error": {"message": "All fields (title, body, category, post_type) are required"}}, 400
        
        # Validate post_type
        if post_type not in ['video', 'audio', 'blog']:
            return {"error": {"message": "Invalid post_type", "field": "post_type"}}, 400

        # Validate category
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            return {"error": {"message": "Category not found", "field": "category"}}, 404

        # Handle thumbnail upload from request.files
        file = request.files.get('thumbnail')
        if not file or not file.content_type.startswith("image/"):
            return {"error": {"message": "Valid thumbnail (image) is required", "field": "thumbnail"}}, 400

        # Upload thumbnail to Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(
                file,
                folder='thumbnails',
                transformation=[{'width': 300, 'height': 300, 'crop': 'thumb', 'radius': 20}]
            )
            thumbnail_url = upload_result['secure_url']
        except Exception as e:
            return {"error": {"message": f"Failed to upload thumbnail: {str(e)}"}}, 500

        # Handle media file upload for video/audio
        media_url = None
        if post_type in ['video', 'audio']:
            media_file = request.files.get('media_file')
            if not media_file or not media_file.content_type.startswith(post_type):
                return {"error": {"message": f"Valid {post_type} file is required", "field": "media_file"}}, 400

            try:
                upload_result = cloudinary.uploader.upload(
                    media_file,
                    resource_type='video' if post_type == 'video' else 'raw',
                    folder=f'media/{post_type}'
                )
                media_url = upload_result['secure_url']
            except Exception as e:
                return {"error": {"message": f"Failed to upload media: {str(e)}"}}, 500

        # Get user from JWT identity
        user_info = get_jwt_identity()
        user_id = user_info["id"]

        # Check if the user exists
        user = User.query.get(user_id)
        if not user:
            return {"error": {"message": "User not found"}}, 404

        # Create new post
        new_post = Post(
            title=title,
            body=body,
            post_type=post_type,
            thumbnail_url=thumbnail_url,
            media_url=media_url,
            user_id=user_id,
            category_id=category.id
        )

        # Save post to the database
        try:
            db.session.add(new_post)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": {"message": f"Database error: {str(e)}"}}, 500

        # Notify category subscribers
        new_post.notify_category_subscribers()

        # Return the created post response
        return {
            "message": "Post created successfully",
            "post": {
                "id": new_post.id,
                "title": new_post.title,
                "category": category_name,
                "post_type": post_type,
                "thumbnail_url": thumbnail_url,
                "media_url": media_url
            }
        }, 201


# Read a post 
class ReadPost(Resource):
    def get(self, post_id):
        post = Post.query.get(post_id)
        if not post:
            return {"message": "Post not found"}, 404
        return {"post": post.serialize_with_comments(page=1, per_page=10, max_depth=3)}, 200

# Like or unlike a post
class LikeTogglePost(Resource):
    @jwt_required()  # Protect this route with JWT authentication
    def post(self, post_id):
        # Get the current user's identity from the JWT token
        user_info = get_jwt_identity()
        user_id = user_info["id"]

        try:
            # Fetch the post by ID
            post = Post.query.get_or_404(post_id)

            # Check if the user has already liked the post
            existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()

            if existing_like:
                # If the user has already liked the post, unlike it
                db.session.delete(existing_like)
                post.likes_count -= 1
                is_liked = False
                message = "Post unliked successfully"
            else:
                # If the user has not liked the post, like it
                new_like = Like(post_id=post_id, user_id=user_id)
                db.session.add(new_like)
                post.likes_count += 1
                is_liked = True
                message = "Post liked successfully"

            db.session.commit()

            # Return a success message
            return {"isLiked": is_liked,"message": message}, 200

        except NoResultFound:
            # Handle case where the post doesn't exist
            return {"message": "Post not found"}, 404
        except Exception as e:
            # General error handling
            return {"message": str(e)}, 500

# Add a comment to a post
class CommentPost(Resource):
    @jwt_required()
    def post(self, post_id):
        # Check if the post exists
        post = Post.query.get(post_id)
        if not post:
            return {"message": "Post not found"}, 404

        # Get comment data from request
        data = request.get_json()
        comment_body = data.get("body")  # 'body' for the comment

        if not comment_body:
            return {"message": "Comment body is required"}, 400

        # Extract user_id from the JWT token
        user_info = get_jwt_identity()

        user_id = user_info['id']

        # Create the new comment
        new_comment = Comment(body=comment_body, post_id=post_id, user_id=user_id)  # Associate user_id with the comment
        db.session.add(new_comment)
        db.session.commit()

        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Paginate comments for the post
        comments_query = Comment.query.filter_by(post_id=post_id).order_by(desc(Comment.created_at))
        paginated_comments = comments_query.paginate(page=page, per_page=per_page, error_out=False)

        # Serialize the comments with replies
        serialized_comments = [
            comment.serialize_with_pagination(page, per_page)
            for comment in paginated_comments.items
        ]

        # Return the new comment and updated list of comments with pagination
        return {
            "message": "Comment added successfully",
            "new_comment": new_comment.id,
            "comments": serialized_comments,
            "pagination": {
                "total_comments": paginated_comments.total,
                "page": page,
                "per_page": per_page,
                "total_pages": paginated_comments.pages
            }
        }, 200



# Admin and Tech writer decorator
def admin_techwriter_role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_info = get_jwt_identity()
            user_id = user_info["id"]
            user = db.session.get(User,user_id)
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
        }, 200

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

        post = db.session.get(Post,post_id)
        if not post:
            return {"error": "Post not found"}, 404
        
        if post.flagged:
            return {"message": "Post is already flagged"}, 200
        
        try:
            post.flagged = True
            db.session.commit()

            # Notify the user that their post was flagged
            flagging_user_id = get_jwt_identity()['id']
            flagging_user = db.session.get(User, flagging_user_id)

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
        post = db.session.get(Post,post_id)
        if not post:
            return {"error": "Post not found"}, 404
        
        if not post.flagged:
            return {"message": "Post is not flagged"}, 200
        
        try:
            post.flagged = False
            db.session.commit()

            flagging_user_id = get_jwt_identity()['id']
            flagging_user = db.session.get(User, flagging_user_id)

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
            user_info = get_jwt_identity()
            user_id = user_info['id']
            user = User.query.get(user_id)
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
    

# Toggle wishlist route
class WishlistTogglePost(Resource):
    @jwt_required()  # Protect this route with JWT authentication
    def post(self, post_id):
        # Get the current user's identity from the JWT token
        user_info = get_jwt_identity()
        user_id = user_info["id"]

        try:
            # Fetch the post by ID
            post = Post.query.get_or_404(post_id)

            # Check if the post is already in the user's wishlist
            existing_wishlist_item = Wishlist.query.filter_by(post_id=post_id, user_id=user_id).first()

            if existing_wishlist_item:
                # If the post is already in the wishlist, remove it
                db.session.delete(existing_wishlist_item)
                is_in_wishlist = False
                message = "Post removed from wishlist successfully"
            else:
                # If the post is not in the wishlist, add it
                new_wishlist_item = Wishlist(post_id=post_id, user_id=user_id)
                db.session.add(new_wishlist_item)
                is_in_wishlist = True
                message = "Post added to wishlist successfully"

            db.session.commit()

            # Return a success message
            return {"isInWishlist": is_in_wishlist, "message": message}, 200

        except Exception as e:
            # General error handling
            return {"message": str(e)}, 500


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

class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "bio": user.bio,
            "profile_pic_url": user.profile_pic_url,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }

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
api.add_resource(FetchAllPostsResource, '/api/allposts', endpoint='allposts')
api.add_resource(CreatePost, '/api/posts/createpost', endpoint='createpost')
api.add_resource(ReadPost, '/api/post/read/<int:post_id>', endpoint='read')
api.add_resource(LikeTogglePost, '/api/post/likeunlike/<int:post_id>', endpoint='likeunlike')
api.add_resource(CommentPost, '/api/post/comment/<int:post_id>', endpoint='comment')
api.add_resource(CategoryResource, '/api/categories/createcategory', endpoint='createcategory')
api.add_resource(ApprovePost, '/api/posts/approve/<int:post_id>', endpoint='approve')
api.add_resource(FlagPost, '/api/posts/flag/<int:post_id>', endpoint='flagpost')
api.add_resource(UnflagPost, '/api/posts/unflag/<int:post_id>', endpoint='unflagpost')
api.add_resource(EditPost, '/api/posts/edit/<int:post_id>', endpoint='editpost')
api.add_resource(SubscribeCategory, '/api/category/subscribe/<int:category_id>', endpoint='subscribecategory')
api.add_resource(UnsubscribeCategory, '/api/category/unsubscribe/<int:category_id>', endpoint='unsubscribecategory')
api.add_resource(WishlistTogglePost, '/api/post/wishlisttoggle/<int:post_id>')
api.add_resource(GetNotifications, '/api/getnotifications', endpoint='getnotifications')
api.add_resource(UserResource, '/api/users/<int:user_id>')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
