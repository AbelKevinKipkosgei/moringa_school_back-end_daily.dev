from datetime import datetime
from sqlalchemy import text
from config import app, db
from models import Notification, User


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

            # Fetch users from the database
            users =  User.query.all()

            if not users:
                print("No users found in the database.")
                return
            
            # Sample notification entries
            notifications = []

            for user in users:
                # Create a notification for each user
                notification_for_user = [
                    Notification(user_id=user.id, message=f"Welcome to the platform, {user.username}!", link="/welcome"),
                    Notification(user_id=user.id, message=f"You have a new follower, {user.username}!", link="/followers"),
                    Notification(user_id=user.id, message=f"New comment on your post, {user.username}!", link="/comments"),
                    Notification(user_id=user.id, message=f"Your post has been approved, {user.username}!", link="/posts"),
                    Notification(user_id=user.id, message=f"New article available in your category, {user.username}!", link="/categories")
                ]
                notifications.extend(notification_for_user)

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