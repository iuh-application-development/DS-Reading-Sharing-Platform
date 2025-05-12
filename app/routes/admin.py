from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User
from app.models.post import Post
from app import db
from functools import wraps
from app.firebase_service import auth

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def initial_admin_required(f):
    @wraps(f)
    @admin_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_initial_admin:
            flash('Chỉ admin initial mới có quyền thực hiện thao tác này.', 'error')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@admin_required
def dashboard():
    users_count = User.query.count()
    posts_count = Post.query.count()
    pending_posts = Post.query.filter_by(status='pending').count()
    return render_template('admin/dashboard.html', 
                         users_count=users_count,
                         posts_count=posts_count,
                         pending_posts=pending_posts)

# Lấy trạng thái user từ firebase
def get_users_with_status():
    users = User.query.all()
    user_status_map = {}

    for u in users:
        fb_user = auth.get_user(u.firebase_uid)
        user_status_map[u.id] = "banned" if fb_user.disabled else "active"

    return user_status_map


@bp.route('/users')
@admin_required
def manage_users():
    users = User.query.filter(User.id != current_user.id).all()
    user_status_map = get_users_with_status()
    return render_template('admin/users.html', users=users, user_status_map = user_status_map)


@bp.route('/user/<int:user_id>/toggle_status', methods=['POST'])
@initial_admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    uid = user.firebase_uid
    if user.is_initial_admin:
        flash('Không thể thay đổi trạng thái của admin initial.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    new_status = request.form.get('status')
    if new_status in ['active', 'banned']:
        try:
            if new_status == 'banned':
                disabled = True
            else:
                disabled = False
            auth.update_user(uid, disabled=disabled )   
        except Exception as e:
            flash(f'Lỗi {e}','error')
        flash(f'Đã cập nhật trạng thái tài khoản của {user.full_name}.', 'success')
    
    return redirect(url_for('admin.manage_users'))

@bp.route('/user/<int:user_id>/toggle_admin', methods=['POST'])
@initial_admin_required
def toggle_admin_role(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.is_initial_admin:
        flash('Không thể thay đổi quyền của admin initial.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    user.role = 'user' if user.role == 'admin' else 'admin'
    db.session.commit()
    flash(f'Đã {"cấp" if user.role == "admin" else "thu hồi"} quyền admin cho {user.username}.', 'success')
    
    return redirect(url_for('admin.manage_users'))

@bp.route('/posts')
@admin_required
def manage_posts():
    posts = Post.query.all()
    return render_template('admin/posts.html', posts=posts)

@bp.route('/post/<int:post_id>/review', methods=['POST'])
@admin_required
def review_post(post_id):
    post = Post.query.get_or_404(post_id)
    action = request.form.get('action')
    
    if action == 'approve':
        post.status = 'approved'
        flash('Bài viết đã được phê duyệt.', 'success')
    elif action == 'reject':
        post.status = 'rejected'
        flash('Bài viết đã bị từ chối.', 'error')
    
    db.session.commit()
    return redirect(url_for('admin.manage_posts'))

@bp.route('/admin_settings')
@initial_admin_required
def admin_settings():
    """Trang quản lý admin dành cho admin initial"""
    admins = User.query.filter_by(role='admin').all()
    users = User.query.filter_by(role='user').all()
    return render_template('admin/admin_settings.html', admins=admins, users=users)

@bp.route('/add_admin', methods=['POST'])
@initial_admin_required
def add_admin():
    user_id = request.form.get('user_id')
    if not user_id:
        flash('Vui lòng chọn người dùng.', 'error')
        return redirect(url_for('admin.admin_settings'))
    
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Người dùng này đã là admin.', 'error')
    else:
        user.role = 'admin'
        db.session.commit()
        flash(f'Đã cấp quyền admin cho {user.username}.', 'success')
    
    return redirect(url_for('admin.admin_settings'))

@bp.route('/dashboard/stats')
@admin_required
def dashboard_stats():
    """API trả về thống kê cho dashboard"""
    total_users = User.query.count()
    total_posts = Post.query.count()
    pending_posts = Post.query.filter_by(status='pending').count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    return {
        'total_users': total_users,
        'total_posts': total_posts,
        'pending_posts': pending_posts,
        'recent_users': [{'username': u.username, 'created_at': u.created_at} for u in recent_users],
        'recent_posts': [{'title': p.title, 'author': p.author.username} for p in recent_posts]
    } 