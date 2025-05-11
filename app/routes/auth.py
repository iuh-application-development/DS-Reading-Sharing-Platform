from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.models.like import Like
from app.models.post import Post

from app import db
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from app.utils.pexels import get_random_avatar

bp = Blueprint('auth', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        login_id = request.form.get('login_id')  # Có thể là username hoặc email
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        # Tìm user theo username hoặc email
        user = User.query.filter(
            (User.username == login_id) | (User.email == login_id)
        ).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Tài khoản của bạn đã bị vô hiệu hóa.', 'error')
                return redirect(url_for('auth.login'))
                
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Tên đăng nhập/email hoặc mật khẩu không đúng.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        bio = request.form.get('bio')
        
        # Kiểm tra mật khẩu xác nhận
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp.', 'error')
            return redirect(url_for('auth.register'))
            
        # Kiểm tra username đã tồn tại
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã được sử dụng.', 'error')
            return redirect(url_for('auth.register'))
            
        # Kiểm tra email đã tồn tại
        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng.', 'error')
            return redirect(url_for('auth.register'))
        
        # Tạo user mới
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            phone=phone,
            date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d').date() if date_of_birth else None,
            gender=gender,
            bio=bio
        )
        
        # Lấy avatar ngẫu nhiên khi tạo user
        new_user.random_avatar_url = get_random_avatar()
        new_user.avatar_updated_at = datetime.utcnow()
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra. Vui lòng thử lại.', 'error')
            
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            # Cập nhật thông tin profile
            current_user.full_name = request.form.get('full_name')
            current_user.bio = request.form.get('bio')
            current_user.phone = request.form.get('phone')
            
            # Xử lý ngày sinh
            date_of_birth = request.form.get('date_of_birth')
            if date_of_birth:
                current_user.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d')
            
            current_user.gender = request.form.get('gender')

            # Xử lý upload avatar nếu có
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and file.filename != '' and allowed_file(file.filename):
                    # Tạo tên file an toàn
                    filename = secure_filename(file.filename)
                    # Thêm timestamp vào tên file để tránh trùng lặp
                    filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    
                    # Lưu file
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    
                    # Xóa avatar cũ nếu có
                    if current_user.avatar_filename:
                        old_file_path = os.path.join(upload_folder, current_user.avatar_filename)
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    
                    # Cập nhật thông tin avatar trong database
                    current_user.avatar_filename = filename
                    current_user.avatar_url = None

            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'message': 'Cập nhật thông tin thành công!',
                    'avatar_url': url_for('static', filename=current_user.get_avatar_path()) if current_user.avatar_filename else current_user.avatar_url
                })
            
            flash('Cập nhật thông tin thành công!', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'error': 'Có lỗi xảy ra khi cập nhật thông tin.'
                }), 400
                
            flash('Có lỗi xảy ra khi cập nhật thông tin.', 'error')
            
    return render_template('auth/profile.html')

@bp.route('/refresh-avatar', methods=['POST'])
@login_required
def refresh_avatar():
    """Làm mới avatar ngẫu nhiên"""
    try:
        new_avatar = get_random_avatar()
        current_user.random_avatar_url = new_avatar
        db.session.commit()
        flash('Đã cập nhật avatar mới!', 'success')
    except Exception as e:
        print(f"Error refreshing avatar: {str(e)}")
        flash('Không thể cập nhật avatar. Vui lòng thử lại.', 'error')
    
    return redirect(url_for('auth.profile')) 

# Chức năng tìm kiếm
@bp.route('/search', methods=['GET'])
def search_posts():
    """Tìm kiếm bài đăng theo tiêu đề, tác giả, hashtag và hiển thị gợi ý"""
    query = request.args.get('query', '').strip()  # Lấy query từ thanh tìm kiếm
    search_type = request.args.get('search_type', 'all')  # Lấy loại tìm kiếm
    suggestions = []
    posts = []
    authors = []

    if query:
        # Chỉ lấy bài đăng đã duyệt
        base_query = Post.query.filter(Post.status == 'approved')

        # Xử lý quyền xem bài viết
        if current_user.is_authenticated:
            if not current_user.is_initial_admin:
                base_query = base_query.filter(
                    db.or_(
                        Post.visibility == 0,  # Công khai
                        db.and_(Post.visibility == 1, Post.user_id == current_user.id)  # Chỉ mình tôi
                    )
                )
        else:
            base_query = base_query.filter(Post.visibility == 0)  # Chỉ hiện bài công khai cho người chưa đăng nhập

        # Các loại tìm kiếm
        if search_type == 'all':
            posts = base_query.filter(
                db.or_(
                    Post.title.ilike(f'%{query}%'),
                    Post.content.ilike(f'%{query}%'),
                    Post.tags.ilike(f'%{query}%')
                )
            ).order_by(Post.created_at.desc()).all()

            # Tìm tác giả luôn
            authors = User.query.filter(
                db.or_(
                    User.username.ilike(f'%{query}%'),
                    User.full_name.ilike(f'%{query}%')
                )
            ).all()

        elif search_type == 'title':
            posts = base_query.filter(Post.title.ilike(f'%{query}%')).order_by(Post.created_at.desc()).all()

        elif search_type == 'author':
            posts = base_query.join(User, Post.user_id == User.id)\
                .filter(db.or_(
                    User.username.ilike(f'%{query}%'),
                    User.full_name.ilike(f'%{query}%')
                ))\
                .order_by(Post.created_at.desc()).all()

            authors = User.query.filter(
                db.or_(
                    User.username.ilike(f'%{query}%'),
                    User.full_name.ilike(f'%{query}%')
                )
            ).all()

        elif search_type == 'hashtag':
            posts = base_query.filter(Post.tags.ilike(f'%{query}%')).order_by(Post.created_at.desc()).all()

        # Gợi ý tìm kiếm (chỉ với bài đã duyệt và có quyền xem)
        suggestions = base_query.filter(
            db.or_(
                Post.title.ilike(f'%{query}%'),
                Post.tags.ilike(f'%{query}%')
            )
        ).order_by(Post.title).limit(5).all()

    # Xử lý likes
    likes = []
    liked_post_ids = []
    total_likes_dict = {}
    
    if current_user.is_authenticated:
        likes = Like.query.filter_by(user_id=current_user.id).all()
        liked_post_ids = [like.post_id for like in likes] if likes else []
        total_likes_query = db.session.query(Like.post_id, db.func.count(Like.post_id).label('like_count'))\
            .group_by(Like.post_id).all()
        total_likes_dict = {post_id: like_count for post_id, like_count in total_likes_query}

    return render_template('main/search.html', 
                     query=query, 
                     search_type=search_type,
                     posts=posts, 
                     suggestions=suggestions, 
                     likes=total_likes_dict,
                     liked_post_ids=liked_post_ids,
                     authors=authors)

@bp.route('/search/suggestion', methods=['POST'])
def select_suggestion():
    """Xử lý khi người dùng chọn một gợi ý"""

    suggestion = request.form.get('suggestion', '').strip()
    if suggestion:
        return redirect(url_for('auth.search_posts', query=suggestion))
    return redirect(url_for('auth.search_posts'))

@bp.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('Không có file được chọn.', 'error')
        return redirect(url_for('auth.profile'))
        
    file = request.files['avatar']
    if file.filename == '':
        flash('Không có file được chọn.', 'error')
        return redirect(url_for('auth.profile'))
        
    if file and allowed_file(file.filename):
        try:
            # Tạo tên file an toàn
            filename = secure_filename(file.filename)
            # Thêm timestamp vào tên file để tránh trùng lặp
            filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            
            # Lưu file
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            
            print(f"Saving file to: {file_path}")  # Debug log
            file.save(file_path)
            print(f"File saved successfully")  # Debug log
            
            # Xóa avatar cũ nếu có
            if current_user.avatar_filename:
                old_file_path = os.path.join(upload_folder, current_user.avatar_filename)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                    print(f"Old avatar removed: {old_file_path}")  # Debug log
            
            # Cập nhật thông tin avatar trong database
            current_user.avatar_filename = filename
            current_user.avatar_url = None  # Reset avatar_url khi có avatar_filename
            
            db.session.commit()
            print(f"Database updated with new avatar: {filename}")  # Debug log
            
            flash('Cập nhật ảnh đại diện thành công!', 'success')
        except Exception as e:
            print(f"Error uploading avatar: {str(e)}")  # Debug log
            db.session.rollback()
            flash('Có lỗi xảy ra khi cập nhật avatar.', 'error')
    else:
        flash('File không hợp lệ. Chỉ chấp nhận file ảnh (PNG, JPG, JPEG, GIF).', 'error')
        
    return redirect(url_for('auth.profile'))

