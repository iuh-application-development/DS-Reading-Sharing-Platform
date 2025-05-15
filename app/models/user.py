from flask import current_app, has_app_context
import os
from app import db
from flask_login import UserMixin
from datetime import datetime
import random
import hashlib
from app.models.saved_post import SavedPost
from app.models.follow import Follow
from app.utils.time_vn import  vn_now
from flask import url_for

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
    created_at = db.Column(db.DateTime, default= vn_now())
    updated_at = db.Column(db.DateTime, default= vn_now(), onupdate= vn_now())
    last_login = db.Column(db.DateTime)

    # Quan hệ followers/following
    following = db.relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        back_populates='follower',  # Link to Follow.follower
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    followers = db.relationship(
        'Follow',
        foreign_keys='Follow.followed_id',
        back_populates='followed',  # Link to Follow.followed
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    comments = db.relationship(
        'Comment',
        back_populates='user',
        cascade='all, delete-orphan',
        passive_deletes=True
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

    # def get_avatar_path(self):
    #     if self.avatar_filename:
    #         # Tạo đường dẫn tương đối cho tệp avatar
    #         avatar_rel_path = f"uploads/avatars/{self.avatar_filename}"
    #         # Tạo URL tĩnh với url_for, thêm tham số phá bộ nhớ đệm
    #         avatar_url = url_for('static', filename=avatar_rel_path, _t=self.updated_at.timestamp() if self.updated_at else random.randint(1, 100000))
            
    #         if has_app_context():
    #             # Tạo đường dẫn đầy đủ để kiểm tra tồn tại
    #             avatar_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'static', 'uploads')), 'avatars', self.avatar_filename)
    #             if os.path.exists(avatar_path):
    #                 current_app.logger.info(f"Đã tìm thấy avatar: {avatar_path}")
    #             else:
    #                 current_app.logger.warning(f"Không tìm thấy tệp avatar: {avatar_path}")
    #         return avatar_url

    #     if self.avatar_url:
    #         return self.avatar_url

    #     self.avatar_url = self.generate_random_avatar()
    #     db.session.commit()
    #     return self.avatar_url
    def get_avatar_path(self):
        if self.avatar_filename:
            # URL public của Firebase Storage dạng:
            # https://storage.googleapis.com/<bucket-name>/avatars/<filename>
            bucket_name = "prjtest-53174.firebasestorage.app"  
            return f"https://storage.googleapis.com/{bucket_name}/avatars/{self.avatar_filename}"

        # Nếu không có file → tạo avatar ngẫu nhiên
        if self.avatar_url is None:
            self.avatar_url = self.generate_random_avatar()
            db.session.commit()
        return self.avatar_url



    @staticmethod
    def generate_random_avatar():
        seed = random.getrandbits(128)
        hash_value = hashlib.md5(str(seed).encode()).hexdigest()
        return f"https://www.gravatar.com/avatar/{hash_value}?d=identicon"