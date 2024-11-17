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
from flask_redis import FlaskRedis
import redis

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urban_mart.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=120)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] =  timedelta(days=30)
app.config['BLACKLIST'] = set()
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['REDIS_URL'] = os.getenv('REDIS_URL')

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

# Setup Flask-Redis for blacklisting
redis_client = FlaskRedis(app)

# Test Cloudinary configuration
try:
    cloudinary.api.ping()
    print("Cloudinary configured successfully")
except Exception as e:
    print(f"Error configuring Cloudinary: ", {e})

# Test redis configuration
try:
    redis_client.ping()
    print(f"Redis connection successful")
except redis.AuthenticationError as e:
    print(f"Redis authentication failed: {e}")
except redis.ConnectionError as e:
    print(f"Redis connection failed: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
