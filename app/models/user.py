from app import db
from flask_login import UserMixin
from datetime import datetime
import random
import hashlib

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Thông tin cá nhân
    full_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(200))
    bio = db.Column(db.Text)
    phone = db.Column(db.String(15))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    
    # Thông tin tài khoản
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    is_initial_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def is_admin(self):
        return self.role == 'admin'

    def can_manage_users(self):
        return self.is_admin() and self.is_initial_admin 

    @property
    def account_status(self):
        return 'banned' if not self.is_active else 'active'

    def generate_avatar_seed(self):
        seed = f"{self.username}_{self.role}_{self.id}"
        return hashlib.md5(seed.encode()).hexdigest()

    def has_saved_post(self, post_id):
        from app.models.saved_post import SavedPost  # import tại đây để tránh circular import
        return SavedPost.query.filter_by(user_id=self.id, post_id=post_id).first() is not None

    @staticmethod
    def generate_random_avatar():
       
        return 'https://avatar.iran.liara.run/public'
