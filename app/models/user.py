from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import random
import os

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Thông tin cá nhân
    full_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(200))
    avatar_filename = db.Column(db.String(200))
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

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # Tự động gán avatar khi tạo user mới
        if not self.avatar_url:
            self.avatar_url = self.generate_avatar_url()

    def generate_avatar_url(self):
        """Tạo URL avatar ngẫu nhiên"""
        # Danh sách các avatar mẫu
        avatar_templates = [
            "https://raw.githubusercontent.com/Ashwinvalento/cartoon-avatar/master/lib/images/male/45.png",
            "https://raw.githubusercontent.com/Ashwinvalento/cartoon-avatar/master/lib/images/female/45.png",
            "https://raw.githubusercontent.com/Ashwinvalento/cartoon-avatar/master/lib/images/male/85.png",
            "https://raw.githubusercontent.com/Ashwinvalento/cartoon-avatar/master/lib/images/female/85.png",
            # Thêm nhiều avatar mẫu khác nếu muốn
        ]
        return random.choice(avatar_templates)

    def is_admin(self):
        return self.role == 'admin'

    def can_manage_users(self):
        return self.is_admin() and self.is_initial_admin 

    @property
    def account_status(self):
        if not self.is_active:
            return 'banned'
        return 'active'

    def generate_avatar_seed(self):
        """Tạo seed cho avatar dựa trên username và role"""
        seed = f"{self.username}_{self.role}_{self.id}"
        return hashlib.md5(seed.encode()).hexdigest()

    def has_saved_post(self, post_id):
        return SavedPost.query.filter_by(
            user_id=self.id,
            post_id=post_id
        ).first() is not None 

    def get_avatar_path(self):
        """Lấy đường dẫn đầy đủ của avatar"""
        if self.avatar_filename:
            return f'uploads/avatars/{self.avatar_filename}'
        return self.avatar_url 