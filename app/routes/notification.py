from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.notification_service import NotificationService
import logging
from functools import wraps

logger = logging.getLogger(__name__)

bp = Blueprint('notification', __name__)

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({'error': str(e)}), 500
    return decorated_function

@bp.route('/notifications')
@login_required
@handle_errors
def get_notifications():
    """Lấy danh sách thông báo của user"""
    logger.info(f"Getting notifications for user {current_user.id}")
    notifications = NotificationService.get_user_notifications(current_user.id)
    logger.info(f"Found {len(notifications)} notifications")
    
    result = [{
        'id': n.id,
        'message': n.message,
        'post_id': n.post_id,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for n in notifications]
    
    logger.info(f"Returning {len(result)} notifications")
    return jsonify(result)

@bp.route('/notifications/unread-count')
@login_required
@handle_errors
def get_unread_count():
    """Lấy số thông báo chưa đọc"""
    logger.info(f"Getting unread count for user {current_user.id}")
    count = NotificationService.get_unread_count(current_user.id)
    logger.info(f"Found {count} unread notifications")
    return jsonify({'count': count})

@bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
@handle_errors
def mark_all_read():
    """Đánh dấu tất cả thông báo là đã đọc"""
    logger.info(f"Marking all notifications as read for user {current_user.id}")
    success = NotificationService.mark_all_as_read(current_user.id)
    if success:
        logger.info("Successfully marked all notifications as read")
        return jsonify({'success': True})
    else:
        logger.error("Failed to mark notifications as read")
        return jsonify({'error': 'Failed to mark notifications as read'}), 500 
    
@bp.route('/notifications/<int:notification_id>/mark-read', methods=['POST'])
@login_required
@handle_errors
def mark_read(notification_id):
    """Đánh dấu một thông báo là đã đọc"""
    logger.info(f"Marking notification {notification_id} as read for user {current_user.id}")
    success = NotificationService.mark_as_read(current_user.id, notification_id)
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to mark notification as read'}), 500
