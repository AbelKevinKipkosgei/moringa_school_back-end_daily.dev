from datetime import datetime
from sqlalchemy import text
from models import Post
from config import app, db

# Function to seed posts
def seed_posts():
    with app.app_context():
        try:
            # Clear existing posts
            db.session.query(Post).delete()
            db.session.commit()
            print("Post table cleared.")

            # Reset the ID sequence to start from 1
            db.session.execute(text("ALTER SEQUENCE posts_id_seq RESTART WITH 1"))
            db.session.commit()

            # Create new posts
            posts = [
                # Post 1
                Post(
                    title="Introduction to Python",
                    post_type="tutorial",
                    body="Learn the basics of Python programming.",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    approved=True,
                    author_id=1,
                    category_id=1,
                    likes_count=10
                ),
                # Post 2
                Post(
                    title="Understanding SQLAlchemy ORM",
                    post_type="tutorial",
                    body="Deep dive into SQLAlchemy ORM for database management.",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    approved=True,
                    author_id=2,
                    category_id=2,
                    likes_count=15
                ),
                #  Post 3
                Post(
                    title="Data Science in 2024",
                    post_type="blog",
                    body="Exploring trends and tools in data science.",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    approved=True,
                    author_id=3,
                    category_id=3,
                    likes_count=25
                ),
                # Post 4
                Post(
                    title="Setting Up Flask Applications",
                    post_type="guide",
                    body="Step-by-step guide to setting up Flask applications.",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    approved=False,
                    author_id=4,
                    category_id=1,
                    likes_count=5
                ),
                #  Post 5
                Post(
                    title="Advanced CSS Techniques",
                    post_type="tutorial",
                    body="Master advanced CSS techniques for responsive design.",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    approved=True,
                    author_id=5,
                    category_id=4,
                    likes_count=8
                ),
                # Post 6
                Post(
                    title="The Future of AI",
                    post_type="blog",
                    body="Predictions and trends for the future of AI.",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    approved=True,
                    author_id=6,
                    category_id=3,
                    likes_count=30
                )
            ]

            # Add each post to the session
            for post in posts:
                db.session.add(post)

            # Commit all changes
            db.session.commit()
            print("Seeded posts successfully.")

        except Exception as e:
            # Rollback if any error occurs
            db.session.rollback()
            print("Failed to seed posts:", str(e))

# Run the seed function
if __name__ == "__main__":
    seed_posts()
