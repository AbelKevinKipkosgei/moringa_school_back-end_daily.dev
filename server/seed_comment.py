from datetime import datetime
from sqlalchemy import text
from models import Comment
from config import app, db

# Function to seed comments
def seed_comments():
    with app.app_context():
        try:
            # Clear existing comments
            db.session.query(Comment).delete()
            db.session.commit()
            print("Comment table cleared.")

            # Reset the ID sequence to start from 1
            db.session.execute(text("ALTER SEQUENCE comments_id_seq RESTART WITH 1"))
            db.session.commit()

            # Create new comments
            comments = [
                # Parent comments for post 1
                Comment(post_id=1, user_id=1, body="Wow, I love this.", created_at=datetime.now()),
                Comment(post_id=1, user_id=2, body="I find the topic quite insightful.", created_at=datetime.now()),
                Comment(post_id=1, user_id=3, body="Here's my take on the subject.", created_at=datetime.now()),

                # Replies to comments on post 1
                Comment(post_id=1, user_id=4, body="Great work!", created_at=datetime.now(), parent_comment_id=1),
                Comment(post_id=1, user_id=5, body="I totally agree with your thoughts!", created_at=datetime.now(), parent_comment_id=2),
                Comment(post_id=1, user_id=6, body="Can you explain that in more detail?", created_at=datetime.now(), parent_comment_id=3),
                Comment(post_id=1, user_id=1, body="Thanks for the reply! I'll elaborate.", created_at=datetime.now(), parent_comment_id=4),

                # Parent comments for post 2
                Comment(post_id=2, user_id=2, body="This post really opened my eyes!", created_at=datetime.now()),
                Comment(post_id=2, user_id=7, body="The examples are really easy to follow.", created_at=datetime.now()),
                Comment(post_id=2, user_id=4, body="Can you clarify a point from this post?", created_at=datetime.now()),

                # Replies to comments on post 2
                Comment(post_id=2, user_id=5, body="Happy to hear it was helpful!", created_at=datetime.now(), parent_comment_id=10),
                Comment(post_id=2, user_id=6, body="Here's the clarification you asked for.", created_at=datetime.now(), parent_comment_id=12),

                # Parent comments for post 3
                Comment(post_id=3, user_id=3, body="First comment on post 3, loving it!", created_at=datetime.now()),
                Comment(post_id=3, user_id=4, body="Some parts were confusing at first.", created_at=datetime.now()),
                Comment(post_id=3, user_id=5, body="This was very helpful, thank you!", created_at=datetime.now()),

                # Replies to comments on post 3
                Comment(post_id=3, user_id=6, body="I had the same feeling initially.", created_at=datetime.now(), parent_comment_id=16),
                Comment(post_id=3, user_id=1, body="Glad it was useful to you!", created_at=datetime.now(), parent_comment_id=17),

                # Parent comments for post 4
                Comment(post_id=4, user_id=1, body="This post really made me think.", created_at=datetime.now()),
                Comment(post_id=4, user_id=7, body="Interesting perspective, I had not considered that.", created_at=datetime.now()),
                Comment(post_id=4, user_id=3, body="This provides a fresh angle on the topic.", created_at=datetime.now()),

                # Replies to comments on post 4
                Comment(post_id=4, user_id=4, body="That's exactly how I felt, thanks for the post.", created_at=datetime.now(), parent_comment_id=16),
                Comment(post_id=4, user_id=5, body="I had a similar reaction! It's definitely thought-provoking.", created_at=datetime.now(), parent_comment_id=17),

                # Parent comments for post 5
                Comment(post_id=5, user_id=6, body="I was struggling to understand this at first.", created_at=datetime.now()),
                Comment(post_id=5, user_id=2, body="The examples provided helped clarify things.", created_at=datetime.now()),
                Comment(post_id=5, user_id=4, body="This is a great introduction to the topic.", created_at=datetime.now()),

                # Replies to comments on post 5
                Comment(post_id=5, user_id=3, body="This is exactly what I needed to get started!", created_at=datetime.now(), parent_comment_id=16),
                Comment(post_id=5, user_id=5, body="Thanks for sharing this, it makes everything clearer.", created_at=datetime.now(), parent_comment_id=17),

                # Parent comment for post 6
                Comment(post_id=6, user_id=6, body="I was initially confused, but now I get it.", created_at=datetime.now()),
                Comment(post_id=6, user_id=1, body="This article helped me understand things much better.", created_at=datetime.now()),

                # Replies to comments on post 6
                Comment(post_id=6, user_id=2, body="Glad it helped! I felt the same way.", created_at=datetime.now(), parent_comment_id=16),
                Comment(post_id=6, user_id=3, body="Thanks for the feedback! I'm happy it clarified things.", created_at=datetime.now(), parent_comment_id=17),
            ]

            # Add each comment to the session
            for comment in comments:
                db.session.add(comment)

            # Commit all changes
            db.session.commit()
            print("Seeded comments successfully.")

        except Exception as e:
            # Rollback if any error occurs
            db.session.rollback()
            print("Failed to seed comments:", str(e))

# Run the seed function
if __name__ == "__main__":
    seed_comments()
