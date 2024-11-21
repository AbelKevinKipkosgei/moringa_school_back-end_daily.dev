import os
import pytest
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Load environment variables
load_dotenv()

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True

db = SQLAlchemy(app)

@pytest.fixture(scope="module")
def test_app():
    """
    Fixture to set up the Flask application for testing.
    """
    with app.app_context():
        yield app  # This will be passed to the tests

@pytest.fixture(scope="module")
def test_client(test_app):
    """
    Fixture to set up a test client for making requests to the app.
    """
    return test_app.test_client()

@pytest.fixture(scope="module")
def init_db():
    """
    Fixture to initialize and clean up the test database.
    """
    with app.app_context():
        db.create_all()  # Create all tables
        yield db  # Provide the database instance to tests
        db.session.remove()
        db.drop_all()  # Clean up the database after tests
