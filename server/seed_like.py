from config import db
from models import Like, User, Post
from sqlalchemy.exc import IntegrityError

def seed_likes():
    try:
        # Fetch some users and posts to link likes to
        user1 = User.query.first()
        user2 = User.query.offset(1).first()
        post1 = Post.query.first()
        post2 = Post.query.offset(1).first()

        # Sample like entries
        like1 = Like(user_id=user1.id, post_id=post1.id)
        like2 = Like(user_id=user2.id, post_id=post2.id)
        like3 = Like(user_id=user1.id, post_id=post2.id)

        # Add likes to session and commit
        db.session.add_all([like1, like2, like3])
        db.session.commit()
        print("Likes seeded successfully.")
    
    except IntegrityError:
        db.session.rollback()
        print("Error seeding likes: Possible data integrity issue.")

if __name__ == "__main__":
    with db.session.begin():
        seed_likes()
