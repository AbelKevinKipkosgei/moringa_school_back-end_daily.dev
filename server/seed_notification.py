from config import db
from models import Notification, User
from sqlalchemy.exc import IntegrityError

def seed_notifications():
    try:
        # Fetch some users to link notifications to
        user1 = User.query.first()
        user2 = User.query.offset(1).first()

        # Sample notification entries
        notification1 = Notification(user_id=user1.id, message="Welcome to the platform!", link="/welcome", read_status=False)
        notification2 = Notification(user_id=user2.id, message="Your post received a new like!", link="/posts/1", read_status=False)
        notification3 = Notification(user_id=user1.id, message="You have a new follower!", link="/followers", read_status=True)

        # Add notifications to session and commit
        db.session.add_all([notification1, notification2, notification3])
        db.session.commit()
        print("Notifications seeded successfully.")
    
    except IntegrityError:
        db.session.rollback()
        print("Error seeding notifications: Possible data integrity issue.")

if __name__ == "__main__":
    with db.session.begin():
        seed_notifications()
