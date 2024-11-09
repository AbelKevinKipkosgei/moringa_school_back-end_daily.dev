from sqlalchemy import Boolean
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from config import db


class Post(db.Model, SerializerMixin):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    post_type = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
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
    likes = db.relationship("Like", back_populates="posts")

    # Serialization rules
    serialize_rules = ("-user.posts", "-category.posts", "-likes.posts")

    def __repr__(self):
        return f"Post ID: {self.id}, Title: {self.title}, Post_type: {self.post_type}, Likes_count{self.likes_count}"
