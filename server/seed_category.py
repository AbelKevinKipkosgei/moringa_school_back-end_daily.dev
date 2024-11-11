from datetime import datetime
from config import app, db
from models import Category

# Function to seed category data
def seed_categories():
    with app.app_context():
        try:
            # Drop existing categories
            drop_categories()

            # Define category entries
            categories = [
                Category(name="Fullstack", description="Resources and content for fullstack development"),
                Category(name="Frontend", description="Tips and tutorials on frontend development"),
                Category(name="Backend", description="Backend development guides and resources"),
                Category(name="Data Science", description="Data science articles and tutorials"),
                Category(name="DevOps", description="Resources for DevOps and CI/CD practices"),
                Category(name="Machine Learning", description="Machine learning projects and guides"),
            ]

            # Add each category to the session
            for category in categories:
                db.session.add(category)

            # Commit all changes
            db.session.commit()
            print("Seeded categories successfully.")

        except Exception as e:
            # If any error occurs
            db.session.rollback()
            print("Failed to seed categories:", str(e))

# Function to drop all categories
def drop_categories():
    try:
        # Delete all categories in the table
        db.session.query(Category).delete()
        db.session.commit()
        print("Dropped all categories successfully.")
    except Exception as e:
        db.session.rollback()
        print("Failed to drop categories:", str(e))

# Run the seed function
if __name__ == "__main__":
    seed_categories()
