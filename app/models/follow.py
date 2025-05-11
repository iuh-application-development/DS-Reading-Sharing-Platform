from app import db
from datetime import datetime

class Follow(db.Model):
    __tablename__ = 'follows'
    
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    follower = db.relationship('User', foreign_keys=[follower_id], backref=db.backref('following', lazy='dynamic'))
    followed = db.relationship('User', foreign_keys=[followed_id], backref=db.backref('followers', lazy='dynamic'))

    def __repr__(self):
        return f'<Follow {self.follower.username} ({self.follower.full_name or "No name"}) -> {self.followed.username} ({self.followed.full_name or "No name"})>'

    def to_dict(self):
        """Chuyển đổi thông tin follow thành dictionary để dễ đọc"""
        return {
            'id': self.id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'follower': {
                'id': self.follower.id,
                'username': self.follower.username,
                'full_name': self.follower.full_name or 'No name',
                'email': self.follower.email
            },
            'followed': {
                'id': self.followed.id,
                'username': self.followed.username,
                'full_name': self.followed.full_name or 'No name',
                'email': self.followed.email
            }
        } 