from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import func
from config import db


class User (db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, default='user')
    profile_pic_url = db.Column(db.Text, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    activated = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Relationship mapping user to posts
    posts = db.relationship('Post', back_populates='user', cascade='all, delete-orphan')

    # Relationship mapping user to likes
    likes = db.relationship('Like', back_populates='user', cascade='all, delete-orphan')

    # Relationship mapping user to subscriptions
    subscriptions = db.relationship('Subscription', back_populates='user', cascade='all, delete-orphan')

    # Relationship mapping user to notifications
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan')

    # Relationship mapping user to comments
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')

    # Many-to-many relationship with Post via Wishlist
    wishlist = db.relationship('Wishlist', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')

    # Association proxy to access categories directly
    subscribed_categories = association_proxy('subscriptions', 'category', creator=lambda category_obj: Subscription(category=category_obj))

    # Association proxy to access posts directly
    liked_posts = association_proxy('likes', 'post', creator=lambda post_obj: Wishlist(post=post_obj))

    serialize_rules = ('-subscriptions.user', '-notifications.user', '-comments.user', '-likes.user', 'wishlist.user',)

    # Password encryption
    @hybrid_property
    def password(self):
        raise AttributeError('Password is not accessible!')
    
    @password.setter
    def password(self, password):
        self._password_hash = generate_password_hash(password)

    # Authenticator
    def authenticate(self, password):
        return check_password_hash(self._password_hash, password)

    def __repr__(self):
        return f'User ID: {self.id}, Username: {self.username}, Role: {self.role}'
    

class Category(db.Model, SerializerMixin):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    subscribed_at = db.Column(db.DateTime, default = db.func.now())

    # Relationship mapping category to posts
    posts = db.relationship('Post', back_populates='category', cascade='all, delete')

    # Relationship mapping category to subscription
    subscriptions = db.relationship('Subscription', back_populates='category', cascade='all, delete')

    # Association proxy
    subscribers = association_proxy('subscriptions', 'user', creator = lambda user_obj: Subscription(user = user_obj, subscribed_at = db.func.now()))

    # Serialization rules
    serialize_rules = ('-posts.category', '-subscriptions.category',)

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"
    
    
class Comment(db.Model, SerializerMixin):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Self-referencing for the threaded replies
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)

    # Relationship mapping comment to user
    user = db.relationship('User', back_populates='comments')
    
    # Relationship mapping comment to post
    post = db.relationship('Post', back_populates='comments')

    # Serialization rules
    serialize_rules = ('-user.comments','-post.comments')

    def serialize_with_pagination(self, page=1, per_page=10, current_depth=1, max_depth=3):
        # Stop serialization if the max depth is reached
        if current_depth > max_depth:
            return {'id': self.id, 'user_id': self.user_id, 'body': self.body, 'created_at': self.created_at, 'replies': []}
        
        # Get the paginated replies
        paginated_replies = self.get_replies(page, per_page) if current_depth < max_depth else {'replies': []}

        # Serialize the comment data
        comment_data = {
            'id': self.id,
            'user_id': self.user_id,
            'body': self.body,
            'created_at': self.created_at,
            'replies': [
                reply.serialize_with_pagination(1, per_page, current_depth + 1, max_depth)
                for reply in paginated_replies['replies']
            ],
            'pagination': {
                'total_replies': paginated_replies['total_replies'],
                'page': paginated_replies['page'],
                'per_page': paginated_replies['per_page'],
                'total_pages': paginated_replies['total_pages']
            }
        }

        return comment_data
    
    def get_replies(self, page=1, per_page=10):
        # Fetch replies based on parent_comment_id
        total_replies = db.session.query(func.count(Comment.id)).filter(Comment.parent_comment_id == self.id).scalar()

        replies_query = Comment.query.filter_by(parent_comment_id=self.id).order_by(Comment.created_at)

        paginated_replies = replies_query.paginate(page, per_page, False)

        return {
            'replies': paginated_replies.items,
            'total_replies': total_replies,
            'page': page,
            'per_page': per_page,
            'total_pages': paginated_replies.pages
        }

    def __repr__(self):
        return f"<Comment ID: {self.id} by User ID: {self.user_id}, body{self.body}>"


class Post(db.Model, SerializerMixin):
    __tablename__ = "posts"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    post_type = db.Column(db.String, nullable=False)
    thumbnail_url = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.Text, nullable=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    approved = db.Column(db.Boolean, default=False, nullable=False)
    flagged = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    likes_count = db.Column(db.Integer, nullable=False, default=0)

    # Relationship mapping post to user
    user = db.relationship("User", back_populates="posts")

    # Relationship mapping post to category
    category = db.relationship("Category", back_populates="posts")

    # Relationship mapping post to likes
    likes = db.relationship("Like", back_populates="post", cascade='all, delete-orphan')

    # Relationship mapping post to comments
    comments = db.relationship("Comment", back_populates="post", cascade='all, delete-orphan')

    # Many-to-many relationship with User via wishlist
    wishlisted_by = db.relationship("Wishlist", back_populates="post", cascade='all, delete-orphan', lazy='dynamic')

    # Association proxy for access to users who wishlisted the post
    wishlisted_by_users = association_proxy('wishlisted_by', 'user', creator=lambda user_obj: Wishlist(user=user_obj))

    # Count the number of users who wishlisted this post
    @property
    def wishlist_count(self):
        return len(self.wishlisted_by)
    
    # Get the current user's ID from the JWT token
    @property
    def is_wishlist_by_user(self):
        user_id = get_jwt_identity()
        return any(wishlist.user_id == user_id for wishlist in self.wishlisted_by)

    # Serializer rules
    serialize_only = ('id', 'title', 'post_type', 'thumbnail_url', 'media_url', 'body', 'created_at', 'updated_at', 'approved', 'flagged', 'likes_count', 'category.id', 'user.id', 'user.username', 'comments.id', 'comments.user_id', 'comments.body', 'comments.created_at', 'likes.id', 'likes.user_id', 'likes.post_id', 'likes.liked_at','wishlist_count', 'is_wishlisted_by_user',)

    # Notify when the post is liked
    def notify_on_like(self, liking_user):
        notification = Notification(
            user_id=self.user_id,
            message=f"Your post '{self.title}' was liked by {liking_user.username}.",
            link=f"/posts/{self.id}"
        )
        db.session.add(notification)
        db.session.commit()

    # Remove notification when the post is unliked
    def remove_like_notification(self, unliking_user):
        notification = Notification.query.filter_by(
            user_id=self.user_id,
            message=f"Your post '{self.title}' was liked by {unliking_user.username}."
        ).first()
        if notification:
            db.session.delete(notification)
            db.session.commit()

    # Notify when a new comment is added
    def notify_on_comment(self, commenting_user, comment):
        notification = Notification(
            user_id=self.user_id,
            message=f"{commenting_user.username} commented on your post: '{comment.body[:50]}...'.",
            link=f"/posts/{self.id}#comments"
        )
        db.session.add(notification)
        db.session.commit()

    # Notify when the post is wishlisted
    def notify_on_wishlist(self, wishlisting_user):
        notification = Notification(
            user_id=self.user_id,
            message=f"{wishlisting_user.username} added your post '{self.title}' to their wishlist.",
            link=f"/posts/{self.id}"
        )
        db.session.add(notification)
        db.session.commit()

    # Remove notification when the post is removed from wishlist
    def remove_wishlist_notification(self, unwishlisting_user):
        notification = Notification.query.filter_by(
            user_id=self.user_id,
            message=f"{unwishlisting_user.username} added your post '{self.title}' to their wishlist."
        ).first()
        if notification:
            db.session.delete(notification)
            db.session.commit()

    # Notify subscribers when a new post is created in a category
    def notify_category_subscribers(self):
        for subscriber in self.category.subscribers:
            notification = Notification(
                user_id=subscriber.id,
                message=f"New post in '{self.category.name}': {self.title}.",
                link=f"/posts/{self.id}"
            )
            db.session.add(notification)
        db.session.commit()

    # Remove notification when a user unsubscribes from a category
    @staticmethod
    def remove_category_subscription_notifications(user, category_name):
        notifications = Notification.query.filter_by(
            user_id=user.id,
            message=f"New post in '{category_name}':"
        ).all()
        for notification in notifications:
            db.session.delete(notification)
        db.session.commit()

    # Notify the post author when their post is flagged
    def notify_on_flag(self, flagging_user, reason):
        notification = Notification(
            user_id=self.user_id,
            message=f"Your post '{self.title}' was flagged by {flagging_user.username} for: {reason}.",
            link=f"/posts/{self.id}"
        )
        db.session.add(notification)
        db.session.commit()

    # Remove notification when the post is unflagged
    def remove_flag_notification(self, flagging_user):
        notification = Notification.query.filter_by(
            user_id=self.user_id,
            message=f"Your post '{self.title}' was flagged by {flagging_user.username}."
        ).first()
        if notification:
            db.session.delete(notification)
            db.session.commit()

    # Notify the post author when their post is deleted
    def notify_on_delete(self, admin_user):
        notification = Notification(
            user_id=self.user_id,
            message=f"Your post '{self.title}' was deleted by {admin_user.username}.",
            link="/notifications"
        )
        db.session.add(notification)
        db.session.commit()


    def __repr__(self):
        return f"Post ID: {self.id}, Title: {self.title}, Post_type: {self.post_type}, Likes_count{self.likes_count}"
    
class Subscription(db.Model, SerializerMixin):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    subscribed_at = db.Column(db.DateTime, default=db.func.now())

    # Relationship mapping subscription to user
    user = db.relationship('User', back_populates='subscriptions')

    # Relationship mapping subscription to category
    category = db.relationship('Category', back_populates='subscriptions')

    # Serialization rules
    serialize_rules = ('-user.subscriptions', '-subscriptions.category')

    def __repr__(self):
        return f'Subscription ID: {self.user_id}, User ID: {self.user_id}, Category ID: {self.category_id}'
    
class Notification(db.Model, SerializerMixin):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    read_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    # Relationship mapping notifications to users
    user = db.relationship('User', back_populates='notifications')

    # Serialization rules
    serialize_rules = ('-user.notifications',)

    def mark_as_read(self):
        self.read_status = True

    def __repr__(self):
        return f"<Notification ID: {self.id}, User ID: {self.user_id}, {'Read' if self.read_status else 'Unread'}>"
    
class Like(db.Model, SerializerMixin):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    liked_at = db.Column(db.DateTime, default=db.func.now())

    # Relationship mapping likes to users
    user = db.relationship('User', back_populates='likes')

    # Relationship mapping likes to posts
    post = db.relationship('Post', back_populates='likes')

    # Serializer rules
    serialize_rules = ('-user.likes', '-post.likes')

    def __repr__(self):
        return f"<Like ID: {self.id} User ID: {self.user_id} Post ID: {self.post_id}>"
    
class Wishlist(db.Model, SerializerMixin):
    __tablename__ = 'wishlist'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'))
    added_on = db.Column(db.DateTime, default=db.func.now())

    # Relationship mapping wishlist to user
    user = db.relationship('User', back_populates = 'wishlist')

    # Relationship mapping wishlist to post
    post = db.relationship('Post', back_populates = 'wishlisted_by')

    # Serializer rules
    serialize_rules = ('-user.wishlist', '-post.wishlisted_by',)

    def __repr__(self):
        return f"<Wishlist ID: {self.id} User ID: {self.user_id} Post ID: {self.post_id}>"