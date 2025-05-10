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
from firebase_admin import credentials, firestore, auth
import firebase_admin
from flask import jsonify


bp = Blueprint('auth', __name__)

# Tao firebase-admin app
cred = credentials.Certificate("firebase-auth.json")
print(cred)
firebase_admin.initialize_app(cred)
firebase_db  = firestore.client()

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
@bp.route('/reset-password', methods=['POST','GET'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        print(email)
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Email không tồn tại','warning')
    return render_template('auth/reset_password.html')
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
@bp.route('/search', methods=['GET', 'POST'])
def search_posts():
    """Tìm kiếm bài đăng theo tiêu đề và hiển thị gợi ý"""
    query = request.args.get('query', '').strip()  # Lấy query từ thanh tìm kiếm
    suggestions = []
    posts = []

    if query:
        # Tìm kiếm bài đăng theo tiêu đề (không phân biệt hoa thường)
        posts = Post.query.filter(
            Post.title.ilike(f'%{query}%'),
            Post.status == 'approved'  # Chỉ hiển thị bài đăng đã được phê duyệt
        ).order_by(Post.created_at.desc()).all()

        # Gợi ý tiêu đề bài đăng
        suggestions = Post.query.filter(
            Post.title.ilike(f'%{query}%'),
            Post.status == 'approved'
        ).order_by(Post.title).limit(5).all()  # Giới hạn 5 gợi ý
    likes = Like.query.filter_by(user_id=current_user.id).all()
    total_likes_query = db.session.query(Like.post_id, db.func.count(Like.post_id).label('like_count'))\
        .group_by(Like.post_id).all()
    total_likes_dict = {post_id: like_count for post_id, like_count in total_likes_query}
    # Nếu không có query, trả về trang tìm kiếm
    return render_template('auth/search.html', query=query, posts=posts, suggestions=suggestions, likes = total_likes_dict)

@bp.route('/search/suggestion', methods=['POST'])
def select_suggestion():
    """Xử lý khi người dùng chọn một gợi ý"""

    suggestion = request.form.get('suggestion', '').strip()
    if suggestion:
        return redirect(url_for('auth.search_posts', query=suggestion))
    return redirect(url_for('auth.search_posts'))

@bp.route('/auth', methods=['POST'])
def authorize():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'message': 'Unauthorized'}), 401

    try:
        # Xác minh token
        token = token[7:]
        decoded_token = auth.verify_id_token(token, check_revoked=True, clock_skew_seconds=60)
        
        # print("Decoded token:", decoded_token)
        # print(f"Headers: {request.headers}")
        # print(f"Payload: {request.get_json()}")

        data = request.get_json()
        email = data.get("email")
        full_name = data.get('full_name')
        phone = data.get('phone')

        # photo = data.get('photo') 

        user = User.query.filter_by(email=email).first()

        if not user:
            user = User(
                    username=email,
                    email=email,
                    password_hash=generate_password_hash(""),
                    full_name=full_name,
                    phone=phone,
                    date_of_birth=None,
                    gender=None,
                    bio=None,
                    avatar_url=User.generate_random_avatar(),  
                    created_at=datetime.utcnow()
                )
            db.session.add(user)
            db.session.commit()

        user.last_login = datetime.utcnow()

        login_user(user, remember=True)
        db.session.commit()

        return jsonify({'status': 'success'})

    except Exception as e:
        print("Lỗi xác thực:", e)
        return jsonify({'message': str(e)}), 401 

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

