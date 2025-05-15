from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, session
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, session
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
# from firebase_admin import credentials, firestore, auth
from app.firebase_service import auth, firebase_bucket
from flask import jsonify
from app.utils.time_vn import vn_now
from flask import send_file
import mimetypes

bp = Blueprint('auth', __name__)



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) 
    return render_template('auth/register.html')

@bp.route('/firebase-login', methods=['POST'])
def firebase_login():
    if not request.is_json:
        flash('Request phải là JSON.', 'error')
        return jsonify({'redirect': url_for('auth.login')}), 400

    data = request.get_json(silent=True) or {}
    status = data.get('status')
    message = data.get('message', '')
    auth_header = request.headers.get('Authorization', '')

    if status == 'success' and auth_header.startswith('Bearer '):
        id_token = auth_header.split(' ', 1)[1]
        try:
            decoded = auth.verify_id_token(id_token)
            firebase_uid = decoded['uid']
            status = auth.get_user(firebase_uid)
            if status.disabled:
                flash('Tài khoản đã bị khóa!', 'warning')
                return jsonify({'redirect': url_for('main.index')}), 401
            # Tìm user dựa trên firebase_uid (không tạo mới)
            user = User.query.filter_by(firebase_uid=firebase_uid).first()
            if user:
                login_user(user)
                flash('Đăng nhập thành công!', 'success')
                return jsonify({'redirect': url_for('main.index')}), 200
            else:
                flash('Tài khoản chưa được đăng ký trên hệ thống.', 'error')
                return jsonify({'redirect': url_for('auth.register')}), 401

        except auth.InvalidIdTokenError:
            current_app.logger.warning('Firebase: Invalid ID token')
            flash('Token không hợp lệ.', 'error')
        except auth.ExpiredIdTokenError:
            current_app.logger.warning('Firebase: Expired ID token')
            flash('Phiên đã hết hạn, vui lòng đăng nhập lại.', 'error')
        except Exception as e:
            current_app.logger.exception(f'Firebase verify error: {e}')
            flash('Xác thực Firebase thất bại.', 'error')

    else:
        flash(message or 'Thông tin đăng nhập không chính xác.', 'error')

    return jsonify({'redirect': url_for('auth.login')}), 401





@bp.route('/firebase-register', methods=['POST'])
def firebase_register_status():
    data = request.get_json(silent=True) or {}
    status = data.get('status')
    message = data.get('message')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if status == 'success':
        id_token = data.get('idToken')
        if not id_token:
            flash('Thiếu id Token để lưu thông tin.', 'error')
            return jsonify({'redirect': url_for('auth.register')}), 400

        try:
            decoded = auth.verify_id_token(id_token)
            uid = decoded['uid']
            email = decoded.get('email')

            # Check nếu user chưa tồn tại
            existing_user = User.query.filter_by(firebase_uid=uid).first()
            if not existing_user:
                # Tạo username duy nhất
                base_username = email.split('@')[0]
                username = base_username
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                new_user = User(
                    firebase_uid=uid,
                    email=email,
                    username=username,
                    full_name=f"{last_name} {first_name}",
                    avatar_url=User.generate_random_avatar(),
                )
                db.session.add(new_user)
                db.session.commit()
                flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            else:
                flash('Tài khoản đã tồn tại.', 'info')

            return jsonify({'redirect': url_for('auth.login')}), 200

        except Exception as e:
            current_app.logger.exception(f'Firebase verify error: {e}')
            flash('Xác thực Firebase thất bại.', 'error')
            return jsonify({'redirect': url_for('auth.register')}), 401

    else:
        flash(message or 'Đăng ký thất bại.', 'error')
        return jsonify({'redirect': url_for('auth.register')}), 400
    
@bp.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        status = data.get('status')

        if status == 'success':
            flash('Kiểm tra địa chỉ email của bạn', 'success')
        else:
            flash(data.get('message', 'Đã có lỗi xảy ra'), 'error')

        return jsonify({'ok': True})
    
    return render_template('auth/forgotPassword.html')
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/profile/<username>')
def profile(username):
    """Xem profile của người dùng"""
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    # Lấy danh sách bài viết của người dùng
    posts = Post.query.filter_by(user_id=user.id)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('auth/user_profile.html', user=user, posts=posts)

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
            if current_user.is_authenticated:
                authors = User.query.filter(
                    db.and_(
                        db.or_(
                            User.username.ilike(f'%{query}%'),
                            User.full_name.ilike(f'%{query}%')
                        ),
                        User.id != current_user.id
                    )
                ).all()
            else:
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
    likes = []
    if current_user.is_authenticated:
        likes = [like.post_id for like in Like.query.filter_by(user_id=current_user.id).all()]
    for post in posts:
            post.total_likes = total_likes_dict.get(post.id, 0)
    return render_template('main/search.html', 
                     query=query, 
                     search_type=search_type,
                     posts=posts, 
                     suggestions=suggestions, 
                     likes=likes,
                     liked_post_ids=liked_post_ids,
                     authors=authors)

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
        firebase_uid = decoded_token['uid']

        data = request.get_json()
        email = data.get("email")
        full_name = data.get('full_name')
        phone = data.get('phone')


        user = User.query.filter_by(email=email).first()

        if not user:
            user = User(
                    username=email,
                    email=email,
                    full_name=full_name,
                    phone=phone,
                    date_of_birth=None,
                    gender=None,
                    bio=None,
                    avatar_url=User.generate_random_avatar(),  
                    created_at= vn_now(),
                    updated_at = vn_now(),
                    firebase_uid = firebase_uid
                )
            db.session.add(user)
            db.session.commit()

        user.last_login = vn_now()

        login_user(user, remember=True)
        db.session.commit()

        return jsonify({'status': 'success'})

    except Exception as e:
        print("Lỗi xác thực:", e)
        return jsonify({'message': str(e)}), 401 

def upload_to_firebase(file, filename):
    try:
        blob = firebase_bucket.blob(f"avatars/{filename}")
        file.stream.seek(0)
        blob.upload_from_file(file.stream, content_type=file.content_type)
        blob.make_public()
        current_app.logger.error(f"Thanh cong")
        return blob.public_url
    except Exception as e:
        current_app.logger.error(f"Firebase Upload Error: {str(e)}")
        return None

@bp.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('Không có file được chọn.', 'error')
        return redirect(url_for('auth.profile', username=current_user.username))

    file = request.files['avatar']
    if file.filename == '':
        flash('Không có file được chọn.', 'error')
        return redirect(url_for('auth.profile', username=current_user.username))

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"

            # Upload lên Firebase Storage
            public_url = upload_to_firebase(file, filename)

            current_user.avatar_url = public_url
            current_user.avatar_filename = None  # Không dùng nữa
            db.session.commit()

            flash('Cập nhật ảnh đại diện thành công!', 'success')
        except Exception as e:
            current_app.logger.error(f"Lỗi khi upload avatar lên Firebase: {str(e)}")
            db.session.rollback()
            flash('Có lỗi xảy ra khi cập nhật avatar.' + str(e), 'error')
    else:
        flash('File không hợp lệ. Chỉ chấp nhận ảnh PNG, JPG, JPEG, GIF.', 'error')

    return redirect(url_for('auth.profile', username=current_user.username))

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.phone = request.form.get('phone')
        current_user.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d') if request.form.get('date_of_birth') else None
        current_user.gender = request.form.get('gender')
        current_user.bio = request.form.get('bio')
        
        # Xử lý avatar
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                try:
                    # Tạo tên file an toàn
                    filename = secure_filename(file.filename)
                    # Thêm timestamp vào tên file để tránh trùng lặp
                    filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    
                    # Lưu file
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, filename)
                    
                    # Xóa avatar cũ nếu có
                    if current_user.avatar_filename:
                        old_file_path = os.path.join(upload_folder, current_user.avatar_filename)
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    
                    # Lưu avatar mới
                    file.save(file_path)
                    upload_to_firebase(file, filename)
                    # Cập nhật thông tin avatar trong database
                    current_user.avatar_filename = filename
                    current_user.avatar_url = None  # Reset avatar_url khi có avatar_filename
                    
                except Exception as e:
                    print(f"Error uploading avatar: {str(e)}")
                    flash('Có lỗi xảy ra khi cập nhật avatar.', 'error')
                    return redirect(url_for('auth.edit_profile'))
        
        try:
            db.session.commit()
            flash('Thông tin cá nhân đã được cập nhật thành công!', 'success')
            return redirect(url_for('auth.profile', username=current_user.username))
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi cập nhật thông tin.', 'error')
            return redirect(url_for('auth.edit_profile'))
    
    return render_template('auth/edit_profile.html', user=current_user)
