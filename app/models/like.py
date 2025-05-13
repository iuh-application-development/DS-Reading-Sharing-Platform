from app import db
from datetime import datetime

class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="CASCADE"), nullable=False )
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id',ondelete="CASCADE"), nullable=False )

    # Đảm bảo mỗi user chỉ thích 1 bài viết 1 lần
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_like'),)