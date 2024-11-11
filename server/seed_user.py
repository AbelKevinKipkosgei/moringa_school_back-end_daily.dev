import os
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv
from config import db, app
from models import User

# Load environment variables from .env file
load_dotenv()

def clear_user_table():
    db.session.query(User).delete()
    db.session.commit()
    print("User table cleared")

def seed_user_table():
    # Clear table before seeding
    clear_user_table()

    # Configuration       
    cloudinary.config( 
        cloudinary_url = os.getenv("CLOUDINARY_URL"),
        secure=True
    )

    # List of users to seed
    users_data = [
        {
            'username': 'abel_soi',
            'email': 'abelkevinkipkosgei@gmail.com',
            'password': 'abelsoi254',
            'role': 'admin',
            'profile_pic_url': 'https://photos.google.com/archive/photo/AF1QipOCd93o3H9N4H56E0hAXXV4YN-za47XwA1QhJ9y',
            'bio': 'Cybersecurity Enthusiast and Tech savvy'
        },
        {
            'username': 'jane_smith',
            'email': 'janesmith@gmail.com',
            'password': 'janesmith001',
            'role': 'admin',
            'profile_pic_url': 'https://cdn.pixabay.com/photo/2016/06/17/09/54/woman-1462986_1280.jpg',
            'bio': 'This is Jane Smith'
        },
        {
            'username': 'john_doe',
            'email': 'johndoe@gmail.com',
            'password': 'johnnyboy254',
            'role': 'tech writer',
            'profile_pic_url': 'https://cdn.pixabay.com/photo/2018/10/15/16/16/man-3749344_1280.jpg',
            'bio': 'Tech writer and enthusiast'
        },
        {
            'username': 'james_bond',
            'email': 'jamesbond@gmail.com',
            'password': 'bond007',
            'role': 'tech writer',
            'profile_pic_url': 'https://cdn.pixabay.com/photo/2016/11/16/19/27/daniel-1829795_1280.jpg',
            'bio': 'Call me bond'
        },
        {
            'username': 'sandra_bullock',
            'email': 'sandrabullock@gmail.com',
            'password': 'sandrabullock123',
            'role': 'user',
            'profile_pic_url': 'https://cdn.pixabay.com/photo/2020/11/26/13/57/sandra-bullock-5779099_960_720.png',
            'bio': 'This is Sandra bullock'
        },
        {
            'username': 'felicity_jones',
            'email': 'felicityjones@gmail.com',
            'password': 'felicityjones668',
            'role': 'user',
            'profile_pic_url': 'https://cdn.pixabay.com/photo/2017/02/01/10/43/felicity-jones-2029557_1280.png',
            'bio': 'This is Felicity Jones'
        },
        {
            'username': 'audrey_hepburn',
            'email': 'audreyhepburn@gmail.com',
            'password': 'audreyhepburn762',
            'role': 'user',
            'profile_pic_url': 'https://cdn.pixabay.com/photo/2018/03/29/11/55/audrey-hepburn-3272062_1280.png',
            'bio': 'This is Audrey Hepburn'
        }
    ]

    for user_data in users_data:
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
        new_user =  User(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            role=user_data['role'],
            profile_pic_url=image_url,
            bio=user_data['bio']
        )

        # Add new user to the session
        db.session.add(new_user)

    # Commit all users at once
    db.session.commit()
    print(f'Users successfully seeded!!')

# Run the seed function within the app context
if __name__ == '__main__':
    with app.app_context():
        seed_user_table()