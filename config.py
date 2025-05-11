import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Cấu hình bảo mật
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # Cấu hình database - sử dụng PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("No DATABASE_URL set in environment")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cấu hình upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Email configuration (if needed)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    
    # Pexels API
    PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')
    if not PEXELS_API_KEY:
        print("Warning: PEXELS_API_KEY not set in .env file")
    
    # Cache config để lưu avatar URL
    AVATAR_CACHE_TIMEOUT = 3600  # 1 giờ