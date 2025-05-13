from datetime import datetime
from app import db

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(30),nullable = False)
    is_read = db.Column(db.Boolean, default=False)  # False = chưa đọc, True = đã đọc
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(20))  # 'follow', 'post', ...
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # id người thực hiện hành động
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('notifications', lazy=True))
    actor = db.relationship('User', foreign_keys=[actor_id])
    post = db.relationship('Post', backref=db.backref('notifications', lazy=True))
    
    def __repr__(self):
        return f'<Notification {self.id}>'
    
    def mark_as_read(self):
        self.is_read = True
        db.session.commit() 