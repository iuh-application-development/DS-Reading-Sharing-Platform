from app import db
from datetime import datetime
from app.utils.time_vn import  vn_now

class SavedPost(db.Model):
    __tablename__ = 'saved_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="CASCADE"), nullable=False )
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id',ondelete="CASCADE"), nullable=False )
    saved_at = db.Column(db.DateTime, default= vn_now())
    
    # Relationships
    user = db.relationship('User', backref=db.backref('saved_posts', lazy=True))
    post = db.relationship(
        'Post',
        back_populates='saved_posts',
        passive_deletes=True
    )
 