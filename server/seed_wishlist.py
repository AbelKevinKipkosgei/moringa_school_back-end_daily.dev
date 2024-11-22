from sqlalchemy import text
from config import db, app
from models import User, Post, Wishlist


def clear_wishlist_table():
    try:
        db.session.query(Wishlist).delete()
        # Reset the ID sequence to start from 1
        db.session.execute(text("ALTER SEQUENCE wishlist_id_seq RESTART WITH 1"))
        db.session.commit()
        print("Wishlist table successfully cleared.")
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing wishlist table: {e}")


def seed_wishlist_table():
    with app.app_context():
        try:
            # clear_wishlist_table()
            # Fetch existing users
            user1 = User.query.filter_by(username="abel_soi").first()  
            user2 = User.query.filter_by(username="jane_smith").first()
            user3 = User.query.filter_by(username="john_doe").first()
            user4 = User.query.filter_by(username="james_bond").first()
            user5 = User.query.filter_by(username="sandra_bullock").first()
            user6 = User.query.filter_by(username="felicity_jones").first()
            user7 = User.query.filter_by(username="audrey_hepburn").first()

            # Fetch existing posts
            post1 = Post.query.first()
            post2 = Post.query.all()[1]
            post3 = Post.query.all()[2]
            post4 = Post.query.all()[3]
            post5 = Post.query.all()[4]

            # Add wishlist entries for users and posts
            wishlist_data = [
                {'user': user1, 'post': post1},
                {'user': user2, 'post': post2},
                {'user': user3, 'post': post3},
                {'user': user1, 'post': post4},
                {'user': user4, 'post': post5},
                {'user': user2, 'post': post1},
                {'user': user5, 'post': post3},
                {'user': user6, 'post': post2},
                {'user': user7, 'post': post4},
                {'user': user1, 'post': post5},
                {'user': user2, 'post': post3},
                {'user': user3, 'post': post1},
                {'user': user4, 'post': post2},
                {'user': user5, 'post': post4},
            ]

            for entry in wishlist_data:
                wishlist_item = Wishlist(
                    user_id=entry['user'].id,
                    post_id=entry['post'].id
                )
                db.session.add(wishlist_item)

            # Commit wishlist data
            db.session.commit()
            print(f'Seeded wishlist successfully.')
        except Exception as e:
            print(f'Error seeding wishlist: {e}')
            db.session.rollback()


if __name__ == '__main__':
    seed_wishlist_table()
