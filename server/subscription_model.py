from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from config import db

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