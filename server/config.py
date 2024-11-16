from datetime import timedelta
import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urban_mart.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=120)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] =  timedelta(days=30)
app.config['BLACKLIST'] = set()
app.config['JWT_SECRET_KEY'] = '44f5a389d54e02e21581ce867d3e630265992562c678367237b7a23f42bfa7cecfa40ea77329dbeb14fb8b195cfa1a8b64e22794acae07ddeb78a55ff3d1719b20e3c4760f63250fc49c30f75298e6e462cd877c7445574569881f1d89bee9589a81773a62621378d63b505514d10e8b5216e5ec7bdcf3a1644b2fe95a69d7823f99c78b93339ec015a812b2af18944a862be3847251debd2ce12aef40dda0fce6c9f45dbe612e05ce28655073397c8c63b18bdd4c98d4d8191551f7703a435e8db12af96bd7d94d5619e39523a8ea04b3827caaa3dc1a520ea805bced27fc9d73989cc94c03004859405601b7ffbdb0cbf9ffcd37386b63cf71e4cd5e29ecc1'
app.json.compact = False

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Initialize SQLAlchemy with custom metadata
db = SQLAlchemy(metadata=metadata)

# Setup Flask-Migrate for database migrations
migrate = Migrate(app,db)

# Setup JWT for authentication
jwt = JWTManager(app)

# Initialize Flask-Restful API
api = Api(app)

# Enable CORS globally
CORS(app, supports_credentials=True)

# Initialize SQLAlchemy with app
db.init_app(app)

# Cloudinary configuration
cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key = os.getenv('CLOUDINARY_API_KEY'),
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
)

# Test Cloudinary configuration
try:
    cloudinary.api.ping()
    print("Cloudinary configured successfully")
except Exception as e:
    print(f"Error configuring Cloudinary: ", {e})