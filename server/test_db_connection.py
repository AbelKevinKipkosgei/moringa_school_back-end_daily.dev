import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def test_connection():
    try:
        # Attempt to connect to the database
        with app.app_context():
            db.create_all()
            print("Connection to the database was successful.")
    except Exception as e:
        print("An error occurred while connecting to the database:")
        print(e)

if __name__ == "__main__":
    test_connection()
