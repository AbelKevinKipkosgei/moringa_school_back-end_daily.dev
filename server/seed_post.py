from datetime import datetime
import cloudinary
import cloudinary.uploader
from sqlalchemy import text
from models import Post, User, Category
from config import app, db


def clear_posts_table():
    # Clear existing posts
    db.session.query(Post).delete()
    db.session.commit()
    print("Post table cleared successfully.")

    # Reset the ID sequence to start from 1
    db.session.execute(text("ALTER SEQUENCE posts_id_seq RESTART WITH 1"))
    db.session.commit()

# Function to seed posts
def seed_posts_table():
    with app.app_context():
        try:
            # clear_posts_table()

            # Fetch users
            user1 = User.query.filter_by(username="abel_soi").first()
            user2 = User.query.filter_by(username="john_doe").first()
            user3 = User.query.filter_by(username="jane_smith").first()

            # Fetch categories
            machine_learning = Category.query.filter_by(name="Machine Learning").first()
            data_science = Category.query.filter_by(name="Data Science").first()
            frontend = Category.query.filter_by(name="Frontend").first()
            backend = Category.query.filter_by(name="Backend").first()

            # Configuration
            cloudinary.config( 
            cloud_name = "dgfolnzcl", 
            api_key = "325447839224753", 
            api_secret = "U64bWoq9hlMWmKhJSkHOx98OAVk",
            secure=True
            )

            # Create new posts
            posts_data = [
                {
                    "title": "Introduction to Python",
                    "post_type": "video",
                    "thumbnail_url": "https://i.pinimg.com/1200x/ed/66/63/ed666327dd3ce274d94f2b3547155891.jpg",
                    "body": "Learn the basics of Python programming.",
                    "approved": True,
                    "user": user1,
                    "category": machine_learning,
                    "likes_count": 20
                },
                {
                    "title": "Data Science with Python",
                    "post_type": "blog",
                    "thumbnail_url": "https://i.pinimg.com/1200x/14/cb/c1/14cbc10e848a3e5e794c11b57bf1ba3c.jpg",
                    "body": "Learn how to use Python for data science.",
                    "approved": True,
                    "user": user1,
                    "category": data_science,
                    "likes_count": 30
                },
                {
                    "title": "Frontend Development with React",
                    "post_type": "video",
                    "thumbnail_url": "https://i.pinimg.com/564x/6a/f7/71/6af771b6ab8d611cbc56d184320f7203.jpg",
                    "body": "Learn the basics of React and frontend development.",
                    "approved": True,
                    "user": user2,
                    "category": frontend,
                    "likes_count": 75
                },
                {
                    "title": "Backend Development with NodeJS",
                    "post_type": "blog",
                    "thumbnail_url": "https://i.pinimg.com/1200x/08/86/77/0886779176db12da5565ca4b9541e2b8.jpg",
                    "body": "Learn the basics of NodeJS and backend development.",
                    "approved": True,
                    "user": user3,
                    "category": backend,
                    "likes_count": 50
                },
                {
                    "title": "JavaScript for Frontend Development",
                    "post_type": "video",
                    "thumbnail_url": "https://i.pinimg.com/564x/0e/4f/dc/0e4fdce8ac22e09688c580e5bc4dcd7d.jpg",
                    "body": "Learn the basics of JavaScript and frontend development.",
                    "approved": True,
                    "user": user2,
                    "category": frontend,
                    "likes_count": 100
                },
                {
                    "title": "The AI Ted Talk",
                    "post_type": "audio",
                    "thumbnail_url": "https://i.pinimg.com/1200x/e8/b5/13/e8b513bb64949c29fe3f34316e2572de.jpg",
                    "body": "Learn about AI and its applications.",
                    "approved": True,
                    "user": user3,
                    "category": machine_learning,
                    "likes_count": 25
                }      
            ]

            # Add each post to the session
            for post_data in posts_data:
                try:
                    upload_result = cloudinary.uploader.upload(
                        post_data['thumbnail_url'],
                        public_id=post_data['title'],
                        transformation=[
                            {"width": 800, "height": 600, "crop": "fill", "radius": 20}
                        ]
                    )

                    # Print URL of the uploaded image
                    image_url = upload_result['secure_url']
                    print(f" Thumbnail uploaded: {image_url}")

                    # Create post with uploaded thumbnail
                    new_post = Post(
                        title=post_data['title'],
                        post_type=post_data['post_type'],
                        thumbnail_url=image_url,
                        body=post_data['body'],
                        approved=post_data['approved'],
                        user_id=post_data['user'].id,
                        category_id=post_data['category'].id,
                        likes_count=post_data['likes_count']
                    )

                    # Add new post to the session
                    db.session.add(new_post)
                except Exception as e:
                    print(f"Error uploading thumbnail for {post_data['title']}: {e}")
                    db.session.rollback()

            # Commit all changes
            db.session.commit()
            print("Seeded posts successfully.")

        except Exception as e:
            # Rollback if any error occurs
            db.session.rollback()
            print("Error seeding posts:", str(e))

# Run the seed function
if __name__ == "__main__":
    seed_posts_table()
