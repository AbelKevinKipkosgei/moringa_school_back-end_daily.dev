from sqlalchemy_serializer import SerializerMixin
from config import db
from datetime import datetime

class Like(db.Model, SerializerMixin):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    liked = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='likes')
    post = db.relationship('Post', back_populates='likes')

    serialize_rules = ('-user.likes', '-post.likes')

    def __repr__(self):
        return f"<Like {self.id} - User {self.user_id} {'liked' if self.liked else 'disliked'} Post {self.post_id}>"

    def toggle_like(self):
        self.liked = not self.liked
