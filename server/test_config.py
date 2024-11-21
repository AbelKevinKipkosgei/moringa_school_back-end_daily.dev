import os

class Config:
    """Base configuration with default settings."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")  # In-memory DB for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret-key"  # Example secret key for testing
    JWT_SECRET_KEY = "test-jwt-secret"  # Example JWT secret for testing
