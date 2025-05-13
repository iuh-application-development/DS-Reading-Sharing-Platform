from app import db
from datetime import datetime
from app.utils.time_vn import vn_now

class Follow(db.Model):
    __tablename__ = 'follows'
    
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="CASCADE"), nullable=False )
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="CASCADE"), nullable=False )
    created_at = db.Column(db.DateTime, default=vn_now)
    
    follower = db.relationship(
    'User',
    foreign_keys=[follower_id],
    back_populates='following',
    passive_deletes=True
    )

    followed = db.relationship(
        'User',
        foreign_keys=[followed_id],
        back_populates='followers',
        passive_deletes=True
    )
