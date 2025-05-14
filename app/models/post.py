from app import db
from datetime import datetime
from app.utils.time_vn import  vn_now

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source_link = db.Column(db.String(500))
    source_content = db.Column(db.Text)
    visibility = db.Column(db.Integer, default=0) #Định__mmber # 0: Công khai, 1: Hạn chế 
    image_url = db.Column(db.String(500))  # Thêm trường lưu đường dẫn ảnh
    
    # Metadata
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default= vn_now())
    updated_at = db.Column(db.DateTime, default= vn_now(), onupdate= vn_now())
    
    # Tags (stored as comma-separated string)
    tags = db.Column(db.String(200))
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="CASCADE"), nullable=False )


    author = db.relationship('User', backref=db.backref('posts', lazy=True), passive_deletes=True)
    likes = db.relationship('Like', backref='post', lazy='dynamic',cascade='all, delete-orphan',
    passive_deletes=True)
    comments = db.relationship(
        'Comment',
        back_populates='post',
        cascade='all, delete-orphan',
        passive_deletes=True,
        lazy='dynamic'
    )
    notifications = db.relationship(
        'Notification',
        back_populates='post',
        cascade='all, delete-orphan',
        passive_deletes=True,
        lazy='dynamic'
    )





    
    def __repr__(self):
        return f'<Post {self.title}>'
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',')] if self.tags else []
    
    def set_tags_list(self, tags_list):
        self.tags = ','.join(tags_list) 