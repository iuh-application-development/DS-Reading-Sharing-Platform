from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.notification_service import NotificationService

bp = Blueprint('notification', __name__)

@bp.route('/notifications')
@login_required
def get_notifications():
    """Lấy danh sách thông báo của user"""
    notifications = NotificationService.get_user_notifications(current_user.id)
    return jsonify([{
        'id': n.id,
        'message': n.message,
        'post_id': n.post_id,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for n in notifications])

@bp.route('/notifications/unread-count')
@login_required
def get_unread_count():
    """Lấy số thông báo chưa đọc"""
    count = NotificationService.get_unread_count(current_user.id)
    return jsonify({'count': count})

@bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Đánh dấu tất cả thông báo là đã đọc"""
    NotificationService.mark_all_as_read(current_user.id)
    return jsonify({'success': True}) 