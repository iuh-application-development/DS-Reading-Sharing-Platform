from app.models.notification import Notification
from app import db
from flask import session
from flask_socketio import emit
import logging
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def create_post_notification(user_id, message, type, post_id):
        """Tạo thông báo mới cho bài viết"""
        try:
            logger.info(f"Creating post notification for user {user_id}, post {post_id}")
            notification = Notification(
                user_id=user_id,
                post_id=post_id,
                message=message,
                type = type
            )
            db.session.add(notification)
            db.session.commit()
            return notification
        except SQLAlchemyError as e:
            db.session.rollback()
            return None
        except Exception as e:
            db.session.rollback()
            return None

    @staticmethod
    def create_notification(user_id, post_id, message):
        """Tạo thông báo mới"""
        try:
            notification = Notification(
                user_id=user_id,
                post_id=post_id,
                message=message
            )
            db.session.add(notification)
            db.session.commit()
            return notification
        except SQLAlchemyError as e:
            db.session.rollback()
            return None
        except Exception as e:
            db.session.rollback()
            return None
    
    @staticmethod
    def get_user_notifications(user_id, limit=10):
        """Lấy danh sách thông báo của user"""
        try:
            notifications = Notification.query.filter_by(user_id=user_id)\
                .order_by(Notification.is_read.asc(), Notification.created_at.desc())\
                .limit(limit)\
                .all()
            logger.info(f"Found {len(notifications)} notifications")
            return notifications
        except SQLAlchemyError as e:
            logger.error(f"Database error getting notifications: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting notifications: {str(e)}")
            return []
    
    @staticmethod
    def get_unread_count(user_id):
        """Đếm số thông báo chưa đọc"""
        try:
            logger.info(f"Getting unread count for user {user_id}")
            count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
            logger.info(f"Found {count} unread notifications")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Database error getting unread count: {str(e)}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error getting unread count: {str(e)}")
            return 0
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Đánh dấu tất cả thông báo là đã đọc"""
        try:
            logger.info(f"Marking all notifications as read for user {user_id}")
            result = Notification.query.filter_by(user_id=user_id, is_read=False)\
                .update({'is_read': True})
            db.session.commit()
            logger.info(f"Successfully marked {result} notifications as read")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error marking notifications as read: {str(e)}")
            db.session.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error marking notifications as read: {str(e)}")
            db.session.rollback()
            return False 