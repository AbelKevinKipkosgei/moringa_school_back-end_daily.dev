import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True

db = SQLAlchemy(app)

class TestRoutes(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.drop_all()

    def test_sample_route(self):
        with app.test_client() as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 404)  # Example assertion

if __name__ == "__main__":
    import unittest
    unittest.main()
