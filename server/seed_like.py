from config import app, db
from models import Like, User, Post
from sqlalchemy import text


def clear_likes_table():
    try:
        db.session.query(Like).delete()
        # Reset the ID sequence to start from 1
        db.session.execute(text("ALTER SEQUENCE like_id_seq RESTART WITH 1"))
        db.session.commit()

        print("Likes table successfully cleared!!")
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing likes table: {e}")

def seed_likes_table():
    try:
        # Fetch some users and posts to link likes to
        user1 = User.query.filter(User.id == 1).first()
        user2 = User.query.filter(User.id == 2).first()
        user3 = User.query.filter(User.id == 3).first()
        post1 = Post.query.filter(Post.id == 1).first()
        post2 = Post.query.filter(Post.id == 2).first()
        post3 = Post.query.filter(Post.id == 3).first()

        # Verify that Users and Posts exists
        if not all([user1, user2, user3, post1, post2, post3]):
            print("One of more Users or Posts do not exist")
            if not user1: print('User with ID 1 does not exist')
            if not user2: print('User with ID 2 does not exist')
            if not user3: print('User with ID 3 does not exist')
            if not post1: print('Post with ID 1 does not exist')
            if not post2: print('Post with ID 2 does not exist')
            if not post3: print('Post with ID 3 does not exist')

        # Sample like entries
        like1 = Like(user_id=user1.id, post_id=post1.id)
        like2 = Like(user_id=user2.id, post_id=post2.id)
        like3 = Like(user_id=user1.id, post_id=post2.id)
        like4 = Like(user_id=user3.id, post_id=post3.id)
        like5 = Like(user_id=user2.id, post_id=post3.id)
        like6 = Like(user_id=user2.id, post_id=post1.id)

        # Add likes to session and commit
        db.session.add_all([like1, like2, like3, like4, like5, like6])
        db.session.commit()
        print("Likes seeded successfully.")
    
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding likes: {e}")

if __name__ == "__main__":
    with app.app_context():
        seed_likes_table()
