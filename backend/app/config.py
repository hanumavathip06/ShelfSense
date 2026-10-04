import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-prod')
    
    # SQLAlchemy
    # Use the pooled connection for the running app
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Flask-Migrate needs the direct connection
    DIRECT_URL = os.environ.get('DIRECT_URL')

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    assert JWT_SECRET_KEY, "JWT_SECRET_KEY is missing from environment"
    
    # Secure Cookies Config
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7) # Phase 3: 7-day expiry
    
    # CORS
    CORS_ORIGIN = os.environ.get('CORS_ORIGIN', 'http://localhost:5173')
