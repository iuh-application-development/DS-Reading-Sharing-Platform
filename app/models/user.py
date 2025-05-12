from app import db
from flask_login import UserMixin
from datetime import datetime
import random
import os
import hashlib
from app.models.saved_post import SavedPost

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # đổi về Integer
    firebase_uid = db.Column(db.String(120), unique=True)


    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    full_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(200))
    avatar_filename = db.Column(db.String(200))
    bio = db.Column(db.Text)
    phone = db.Column(db.String(15))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    
    role = db.Column(db.String(20), default='user')
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
        return SavedPost.query.filter_by(user_id=self.id, post_id=post_id).first() is not None

    def get_avatar_path(self):
        if self.avatar_filename:
            return os.path.join('uploads', 'avatars', self.avatar_filename)
        return self.avatar_url or None

    @staticmethod
    def generate_random_avatar():
        seed = random.getrandbits(128)
        hash_value = hashlib.md5(str(seed).encode()).hexdigest()
        return f"https://www.gravatar.com/avatar/{hash_value}?d=identicon"
