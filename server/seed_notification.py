from datetime import datetime
from sqlalchemy import text
from config import app, db
from models import Notification


def clear_notifications_table():
    # Clear existing notifications
    db.session.query(Notification).delete()
    db.session.commit()
    print("Notification table cleared successfully.")

    # Reset the ID sequence to start from 1 for notifications
    db.session.execute(text("ALTER SEQUENCE notifications_id_seq RESTART WITH 1"))
    db.session.commit()

def seed_notifications_table():
    with app.app_context():
        try:
            # clear_notifications_table()
            # Sample notification entries
            notifications = [
                Notification(user_id=1, message="Welcome to the platform!", link="/welcome"),
                Notification(user_id=2, message="Your post has received a new comment.", link="/posts"),
                Notification(user_id=3, message="New subscription!", link="/subscriptions"),
                Notification(user_id=4, message="New article available in your category!", link="/categories"),
                Notification(user_id=5, message="Your post received a like!", link="/posts"),
                Notification(user_id=6, message="Removed like", link="/likes"),
                Notification(user_id=7, message="New post!", link="/posts"),
            ]

              # Add each notification to the session
            for notification in notifications:
                db.session.add(notification)

            # Commit all changes
            db.session.commit()
            print("Seeded notifications successfully.")

        except Exception as e:
            # if any error occurs
            db.session.rollback()
            print("Error seeding notifications:", str(e))

# Run the seed function
if __name__ == "__main__":
    seed_notifications_table()