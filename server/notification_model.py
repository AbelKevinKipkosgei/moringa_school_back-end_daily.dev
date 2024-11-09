from sqlalchemy_serializer import SerializerMixin
from config import db
from datetime import datetime

class Notification(db.Model, SerializerMixin):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notifications')

    serialize_rules = ('-user.notifications',)

    def __repr__(self):
        return f"<Notification {self.id} for User {self.user_id} - {'Read' if self.is_read else 'Unread'}>"

    def mark_as_read(self):
        self.is_read = True
