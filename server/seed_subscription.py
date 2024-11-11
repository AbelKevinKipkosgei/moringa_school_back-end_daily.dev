from datetime import datetime
from sqlalchemy import text
from config import app, db
from models import Subscription

# Function to seed subscription data
def seed_subscriptions():
    with app.app_context():
        try:
            # Clear existing subscriptions
            db.session.query(Subscription).delete()
            db.session.commit()
            print("Subscription table cleared.")

            # Reset the ID sequence to start from 1 for subscriptions
            db.session.execute(text("ALTER SEQUENCE subscriptions_id_seq RESTART WITH 1"))
            db.session.commit()

            # Subscription entries
            subscriptions = [
                Subscription(user_id=1, category_id=1, subscribed_at=datetime.now()),
                Subscription(user_id=1, category_id=2, subscribed_at=datetime.now()),
                Subscription(user_id=2, category_id=1, subscribed_at=datetime.now()),
                Subscription(user_id=2, category_id=3, subscribed_at=datetime.now()),
                Subscription(user_id=3, category_id=2, subscribed_at=datetime.now()),
                Subscription(user_id=4, category_id=1, subscribed_at=datetime.now()),
                Subscription(user_id=5, category_id=3, subscribed_at=datetime.now()),
                Subscription(user_id=6, category_id=1, subscribed_at=datetime.now()),
                Subscription(user_id=6, category_id=2, subscribed_at=datetime.now()),
                Subscription(user_id=7, category_id=4, subscribed_at=datetime.now()),
            ]

            # Add each subscription to the session
            for subscription in subscriptions:
                db.session.add(subscription)

            # Commit all changes
            db.session.commit()
            print("Seeded subscriptions successfully.")

        except Exception as e:
            # Rollback if any error occurs
            db.session.rollback()
            print("Failed to seed subscriptions:", str(e))

# Run the seed function
if __name__ == "__main__":
    seed_subscriptions()
