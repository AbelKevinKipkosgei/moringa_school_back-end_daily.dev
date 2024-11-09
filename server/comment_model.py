from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app import db
from sqlalchemy_serializer import SerializerMixin

class Comment(db.Model,SerializerMixin):
    __tablename__ = 'comments'

    # Fields to include in serialized output
    serialize_rules = ('-user.comments', '-post.comments', '-comments.parent') 

    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Self-referencing for the threaded replies
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)  # Reference for replies

    # Relationships
    user = db.relationship('User', back_populates='comments')  # Link to User who created the comment
    post = db.relationship('Post', back_populates='comments')  # Link to Post this comment belongs to
    parent = db.relationship('Comment', remote_side=[id], backref='comments')  # Self-reference for nested replies

    def __repr__(self):
        return f"<Comment {self.id} by User {self.user_id} , body{self.body}>"

