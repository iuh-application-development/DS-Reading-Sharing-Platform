from app.models.notification import Notification
from app import db
from flask import session

class NotificationService:
    @staticmethod
    def create_notification(user_id, post_id, message):
        """Tạo thông báo mới"""
        notification = Notification(
            user_id=user_id,
            post_id=post_id,
            message=message
        )
        db.session.add(notification)
        db.session.commit()
        
        # Kiểm tra nếu user đang online thì gửi thông báo realtime
        # if session.get('user_id') == user_id:
        #     emit('new_notification', {
        #         'id': notification.id,
        #         'message': message,
        #         'post_id': post_id,
        #         'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
        #     }, room=str(user_id))
        
        # return notification
    
    @staticmethod
    def get_user_notifications(user_id, limit=10):
        """Lấy danh sách thông báo của user"""
        return Notification.query.filter_by(user_id=user_id)\
            .order_by(Notification.is_read.asc(), Notification.created_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_unread_count(user_id):
        """Đếm số thông báo chưa đọc"""
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Đánh dấu tất cả thông báo là đã đọc"""
        Notification.query.filter_by(user_id=user_id, is_read=False)\
            .update({'is_read': True})
        db.session.commit() 