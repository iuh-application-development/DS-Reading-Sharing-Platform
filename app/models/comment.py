from app import db
from datetime import datetime
from app.utils.time_vn import vn_now
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default= vn_now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id',ondelete="CASCADE"), nullable=False)

    # Thêm relationship với User
    user = db.relationship(
        'User',
        back_populates='comments',
        passive_deletes=True
    )

    post = db.relationship(
        'Post',
        back_populates='comments',
        passive_deletes=True
    )

