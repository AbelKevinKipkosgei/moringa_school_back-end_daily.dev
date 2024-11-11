from sqlalchemy_serializer import SerializerMixin
from config import db

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
