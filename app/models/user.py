from flask import current_app, has_app_context
import os
from app import db
from flask_login import UserMixin
from datetime import datetime
import random
import hashlib
from app.models.saved_post import SavedPost
from app.models.follow import Follow

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    # Quan hệ followers/following
    following = db.relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        back_populates='follower',  # Link to Follow.follower
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    followers = db.relationship(
        'Follow',
        foreign_keys='Follow.followed_id',
        back_populates='followed',  # Link to Follow.followed
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

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
            if has_app_context():
                avatar_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'static/uploads'), 'avatars', self.avatar_filename)
                if os.path.exists(avatar_path):
                    current_app.logger.info(f"Avatar found: {avatar_path}")
                    return f"uploads/avatars/{self.avatar_filename}"
                else:
                    current_app.logger.warning(f"Avatar file not found: {avatar_path}")
            else:
                return f"uploads/avatars/{self.avatar_filename}"
        
        if self.avatar_url:
            return self.avatar_url
        
        self.avatar_url = self.generate_random_avatar()
        db.session.commit()
        return self.avatar_url

    @staticmethod
    def generate_random_avatar():
        seed = random.getrandbits(128)
        hash_value = hashlib.md5(str(seed).encode()).hexdigest()
        return f"https://www.gravatar.com/avatar/{hash_value}?d=identicon"