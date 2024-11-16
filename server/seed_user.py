import cloudinary
import cloudinary.uploader
from sqlalchemy import text
from config import db, app
from models import User, Post, Like, Comment, Subscription, Notification, Category


def clear_users_table():
    try:
        db.session.query(User).delete()
        # Reset the ID sequence to start from 1
        db.session.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1"))
        db.session.commit()
        print("User table successfully cleared.")
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing users table: {e}")

def seed_users_table():
    with app.app_context():
        try:
            # Clear table before seeding
            # clear_users_table()

            # Configuration
            cloudinary.config( 
            cloud_name = "dgfolnzcl", 
            api_key = "325447839224753", 
            api_secret = "U64bWoq9hlMWmKhJSkHOx98OAVk",
            secure=True
            )

            # Fetch categories to assign users
            frontend = Category.query.filter_by(name="Frontend").first()
            backend = Category.query.filter_by(name="Backend").first()
            fullstack = Category.query.filter_by(name="Fullstack").first()
            data_science = Category.query.filter_by(name="Data Science").first()
            machine_learning = Category.query.filter_by(name="Machine Learning").first()
            devops = Category.query.filter_by(name="DevOps").first()


            # List of users to seed
            users_data = [
                {
                    'username': 'abel_soi',
                    'email': 'abelkevinkipkosgei@gmail.com',
                    'password': 'abelsoi254',
                    'role': 'admin',
                    'profile_pic_url': 'https://cdn.pixabay.com/photo/2020/01/07/23/01/sketch-4748895_1280.jpg',
                    'bio': 'Cybersecurity Enthusiast and Tech savvy',
                    'categories': [frontend, backend, devops]
                },
                {
                    'username': 'jane_smith',
                    'email': 'janesmith@gmail.com',
                    'password': 'janesmith001',
                    'role': 'admin',
                    'profile_pic_url': 'https://cdn.pixabay.com/photo/2016/06/17/09/54/woman-1462986_1280.jpg',
                    'bio': 'This is Jane Smith',
                    'categories': [data_science, machine_learning]
                },
                {
                    'username': 'john_doe',
                    'email': 'johndoe@gmail.com',
                    'password': 'johnnyboy254',
                    'role': 'techwriter',
                    'profile_pic_url': 'https://cdn.pixabay.com/photo/2018/10/15/16/16/man-3749344_1280.jpg',
                    'bio': 'Tech writer and enthusiast',
                    'categories': [fullstack]
                },
                {
                    'username': 'james_bond',
                    'email': 'jamesbond@gmail.com',
                    'password': 'bond007',
                    'role': 'techwriter',
                    'profile_pic_url': 'https://cdn.pixabay.com/photo/2016/11/16/19/27/daniel-1829795_1280.jpg',
                    'bio': 'Call me bond',
                    'categories': [fullstack, backend, devops]
                },
                {
                    'username': 'sandra_bullock',
                    'email': 'sandrabullock@gmail.com',
                    'password': 'sandrabullock123',
                    'role': 'user',
                    'profile_pic_url': 'https://cdn.pixabay.com/photo/2020/11/26/13/57/sandra-bullock-5779099_960_720.png',
                    'bio': 'This is Sandra bullock',
                    'categories': [data_science, devops]
                },
                {
                    'username': 'felicity_jones',
                    'email': 'felicityjones@gmail.com',
                    'password': 'felicityjones668',
                    'role': 'user',
                    'profile_pic_url': 'https://cdn.pixabay.com/photo/2017/02/01/10/43/felicity-jones-2029557_1280.png',
                    'bio': 'This is Felicity Jones',
                    'categories': [machine_learning, devops]
                },
                {
                    'username': 'audrey_hepburn',
                    'email': 'audreyhepburn@gmail.com',
                    'password': 'audreyhepburn762',
                    'role': 'user',
                    'profile_pic_url': 'https://cdn.pixabay.com/photo/2018/03/29/11/55/audrey-hepburn-3272062_1280.png',
                    'bio': 'This is Audrey Hepburn',
                    'categories': [fullstack, frontend]
                }
            ]

            for user_data in users_data:
                try:
                    # Upload an image
                    upload_result = cloudinary.uploader.upload(
                        user_data['profile_pic_url'],
                        public_id=user_data['username'],
                        transformation=[
                            {
                                'crop': 'thumb', # This will crop the image to a square
                                'gravity': 'face', # Focus on the face if present
                                'width': 200, # The width of the image
                                'height': 200, # The height of the image
                                'radius': 'max', # Apply the circular transformation
                            }
                        ]
                    )

                    # Print URL of the uploaded image
                    image_url = upload_result['secure_url']
                    print(f"Uploaded Image URL for {user_data['username']}: {image_url}")

                    # Create a user with the uploaded image
                    new_user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        role=user_data['role'],
                        profile_pic_url=image_url,
                        bio=user_data['bio']
                    )

                    # Hash password
                    new_user.password=user_data['password']

                    # Assign categories using association proxy
                    new_user.subscribed_categories=user_data['categories']

                    # Add new user to the session
                    db.session.add(new_user)
                except Exception as e:
                    print(f"Error uploading image for {user_data['username']}: {e}")
                    db.session.rollback()

            # Commit all users at once
            db.session.commit()
            print(f'Seeded users successfully.')
        except Exception as e:
            print(f'Error seeding users: {e}')
            db.session.rollback()


if __name__ == '__main__':
    seed_users_table()
