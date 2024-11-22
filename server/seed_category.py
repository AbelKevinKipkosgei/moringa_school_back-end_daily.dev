from sqlalchemy import text
from config import app, db
from models import Category, User, Post


# Function to clear all categories
def clear_categories_table():
    try:
        # Delete all categories in the table
        db.session.query(Category).delete()
        # Reset the ID sequence to start from 1
        db.session.execute(text("ALTER SEQUENCE categories_id_seq RESTART WITH 1"))
        db.session.commit()
        print("Categories table successfully cleared.")
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing categories table: {e}")

# Function to seed category data
def seed_categories_table():
    with app.app_context():
        try:
            # Clear existing categories
            # clear_categories_table()

            # Define category entries
            categories_data = [
                Category(name="Fullstack", description="Resources and content for fullstack development"),
                Category(name="Frontend", description="Tips and tutorials on frontend development"),
                Category(name="Backend", description="Backend development guides and resources"),
                Category(name="Data Science", description="Data science articles and tutorials"),
                Category(name="DevOps", description="Resources for DevOps and CI/CD practices"),
                Category(name="Machine Learning", description="Machine learning projects and guides"),
            ]

            # Create and add each category
            categories = []
            for category_data in categories_data:
                category = Category(name=category_data.name, description=category_data.description)
                db.session.add(category)
                categories.append(category)

            # Commit categories first
            db.session.commit()
            print("Seeded categories successfully.")

            # Fetch users
            user1 = User.query.filter_by(id=1).first()
            user2 = User.query.filter_by(id=2).first()
            user3 = User.query.filter_by(id=3).first()
            user4 = User.query.filter_by(id=4).first()
            user5 = User.query.filter_by(id=5).first()
            user6 = User.query.filter_by(id=6).first()

            # Add subscribers to each category
            categories[0].subscribers.extend([user1, user2])
            categories[1].subscribers.extend([user1, user3, user4, user5])
            categories[2].subscribers.extend([user1, user4, user5])
            categories[3].subscribers.append(user3)
            categories[4].subscribers.extend([user2, user3])
            categories[5].subscribers.append(user1)

            # Commit the subscriptions
            db.session.commit()
            print("Seeded subscribers successfully.")

        except Exception as e:
            # If any error occurs
            db.session.rollback()
            print("Error seeding categories:", str(e))

# Run the seed function
if __name__ == "__main__":
    seed_categories_table()