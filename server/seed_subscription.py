from sqlalchemy import text
from config import app, db
from models import Subscription, User, Category


def clear_subscriptions_table():
    db.session.query(Subscription).delete()
    db.session.commit()
    db.session.execute(text("ALTER SEQUENCE subscriptions_id_seq RESTART WITH 1"))
    db.session.commit()
    print("Subscriptions table cleared successfully.")

def seed_subscriptions_table():
    with app.app_context():
        try:
            # Ensure table is clear before seeding
            clear_subscriptions_table()

            # Fetch users and categories from the database
            users = {
                'abel_soi': User.query.filter_by(username='abel_soi').first(),
                'jane_smith': User.query.filter_by(username='jane_smith').first(),
                'john_doe': User.query.filter_by(username='john_doe').first(),
                'james_bond': User.query.filter_by(username='james_bond').first(),
                'sandra_bullock': User.query.filter_by(username='sandra_bullock').first(),
                'felicity_jones': User.query.filter_by(username='felicity_jones').first(),
                'audrey_hepburn': User.query.filter_by(username='audrey_hepburn').first()
            }

            categories = {
                'Fullstack': Category.query.filter_by(name='Fullstack').first(),
                'Backend': Category.query.filter_by(name='Backend').first(),
                'Frontend': Category.query.filter_by(name='Frontend').first(),
                'DevOps': Category.query.filter_by(name='DevOps').first(),
                'Data Science': Category.query.filter_by(name='Data Science').first(),
                'Machine Learning': Category.query.filter_by(name='Machine Learning').first()
            }

            # Ensure all users and categories exist
            missing_users = [username for username, user in users.items() if user is None]
            missing_categories = [name for name, category in categories.items() if category is None]
            if missing_users or missing_categories:
                raise ValueError(f"Missing users: {missing_users}, Missing categories: {missing_categories}")

            # Define subscriptions data to seed
            subscriptions_data = [
                (users['abel_soi'].id, categories['Machine Learning'].id),
                (users['abel_soi'].id, categories['Fullstack'].id),
                (users['jane_smith'].id, categories['Frontend'].id),
                (users['jane_smith'].id, categories['Backend'].id),
                (users['john_doe'].id, categories['Data Science'].id),
                (users['james_bond'].id, categories['DevOps'].id),
                (users['sandra_bullock'].id, categories['Machine Learning'].id),
                (users['felicity_jones'].id, categories['Frontend'].id),
                (users['felicity_jones'].id, categories['DevOps'].id),
                (users['audrey_hepburn'].id, categories['Data Science'].id)
            ]

            # Seed subscriptions
            for user_id, category_id in subscriptions_data:
                subscription = Subscription(
                    user_id=user_id,
                    category_id=category_id
                )
                db.session.add(subscription)

            # Commit all changes to the database
            db.session.commit()
            print("Subscriptions table seeded successfully.")

        except Exception as e:
            # Rollback in case of error
            db.session.rollback()
            print("Error seeding subscriptions:", str(e))


# Run the seed function
if __name__ == "__main__":
    seed_subscriptions_table()

