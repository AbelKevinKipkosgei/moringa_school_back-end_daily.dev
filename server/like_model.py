from sqlalchemy_serializer import SerializerMixin
from config import db
from datetime import datetime

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
