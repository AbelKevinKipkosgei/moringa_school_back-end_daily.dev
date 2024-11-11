from datetime import datetime
from sqlalchemy import text
from config import app, db
from models import Category

# Function to clear and reset the category table
def clear_category_table():
    try:
        db.session.query(Category).delete()
        # Reset the ID sequence to start from 1
        db.session.execute(text("ALTER SEQUENCE categories_id_seq RESTART WITH 1"))
        db.session.commit()
        print("Category table successfully cleared!")
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing categories table: {e}")

# Function to seed category data
def seed_categories():
    try:
        # First, clear the categories table
        clear_category_table()

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
        # If any error occurs, roll back
        db.session.rollback()
        print(f"Failed to seed categories: {e}")

# Run the seed function
if __name__ == "__main__":
    with app.app_context():
        seed_categories()
