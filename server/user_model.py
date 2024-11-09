from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from config import db
from server.subscription_model import Subscription

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
    serialize_rules = ('posts.user', 'comments.user', 'likes.user','subscriptions.user', 'notifications.user')

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