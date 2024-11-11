from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from config import db

class User (db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, default='user')
    profile_pic_url = db.Column(db.Text, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Relationship mapping user to posts
    posts = db.relationship('Post', back_populates='user', cascade='all, delete-orphan')

    # Relationship mapping user to comments
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')

    # Relationship mapping user to likes
    likes = db.relationship('Like', back_populates='user', cascade='all, delete-orphan')

    # Relationship mapping user to subscriptions
    subscriptions = db.relationship('Subscription', back_populates='user', cascade='all, delete-orphan')

    # Relationship mapping user to notifications
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan')

    # Association proxy to access categories directly
    subscribed_categories = association_proxy('subscriptions', 'category', creator=lambda category_obj: Subscription(category=category_obj))

    # Serialization rules
    serialize_rules = ('-posts.user', '-comments.user', '-likes.user','-subscriptions.user', '-notifications.user')

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
    serialize_rules = ('-user.subscriptions', '-category.subscriptions')

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
    
class Category(db.Model, SerializerMixin):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    subscribed_at = db.Column(db.DateTime, default = db.func.now())

    # Relationship mapping category to posts
    posts = db.relationship('Post', back_populates='category')

    # Relationship mapping category to subscription
    subscriptions = db.relationship('Subscription', back_populates='category')

    # Association proxy
    subscribers = association_proxy('subscriptions', 'user', creator = lambda user_obj: Subscription(user = user_obj, subscribed_at = db.func.now()))

    # Serialization rules
    serialize_rules = ('-posts.category', '-subscriptions.category')

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
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)  # Reference for replies

    # Relationship mapping comment to user
    user = db.relationship('User', back_populates='comments') # Link to the User who made the comment
    
    # Relationship mapping comment to post
    post = db.relationship('Post', back_populates='comments')  # Link to Post this comment belongs to

    # Self-referencing relationships between comment and replies
    parent = db.relationship('Comment', remote_side=[id], back_populates='replies')
    replies = db.relationship('Comment', back_populates='parent')

    # Serialization rules
    serialize_rules = ('-user.comments', '-post.comments', '-replies.parent')

    def __repr__(self):
        return f"<Comment ID: {self.id} by User ID: {self.user_id}, body{self.body}>"
    
class Post(db.Model, SerializerMixin):
    __tablename__ = "posts"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    post_type = db.Column(db.String, nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    approved = db.Column(db.Boolean, default=False)
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

    # Serialization rules
    serialize_rules = ("-user.posts", "-category.posts", "-likes.post", "-comments.post")

    def __repr__(self):
        return f"Post ID: {self.id}, Title: {self.title}, Post_type: {self.post_type}, Likes_count{self.likes_count}"
    
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