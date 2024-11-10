from config import db
from sqlalchemy_serializer import SerializerMixin

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

