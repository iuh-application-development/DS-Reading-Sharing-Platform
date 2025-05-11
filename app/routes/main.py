from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.like import Like
from app.models.post import Post
from app.models.user import User
from app.models.comment import Comment
from app.models.saved_post import SavedPost
from werkzeug.utils import secure_filename
import os
from app import db
from datetime import datetime
from app.models.follow import Follow

bp = Blueprint('main', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    """Trang chủ - hiển thị tất cả bài viết"""
    page = request.args.get('page', 1, type=int)
    
    query = Post.query.order_by(Post.created_at.desc())
    likes = []
    # Nếu không phải admin
    if current_user.is_authenticated and not current_user.is_initial_admin:
        query = query.filter(
            db.or_(
                Post.visibility == 0,  # Công khai
                db.and_(Post.visibility == 1, Post.user_id == current_user.id)  # Chỉ mình tôi
            )
        )
        likes = Like.query.filter_by(user_id=current_user.id).all()

    elif not current_user.is_authenticated:
        query = query.filter(Post.visibility == 0)
    
    # Phân trang
    posts = query.paginate(page=page, per_page=10, error_out=False)
    liked_post_ids = [like.post_id for like in likes] if likes else []
    total_likes_query = db.session.query(Like.post_id, db.func.count(Like.post_id).label('like_count'))\
        .group_by(Like.post_id).all()
    total_likes_dict = {post_id: like_count for post_id, like_count in total_likes_query}
    
    # Gắn tổng số lượt thích vào từng post
    for post in posts.items:
        post.total_likes = total_likes_dict.get(post.id, 0)  # Mặc định 0 nếu không có lượt thích
    return render_template('main/index.html', posts=posts, likes=liked_post_ids)

@bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    """Tạo bài viết mới"""
    if current_user.is_admin():
        flash('Admin không được phép đăng bài.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        source_link = request.form.get('source_link')
        source_content = request.form.get('source_content')
        tags = request.form.get('tags')
        visibility = request.form.get('visibility')
        
        if not title or not content:
            flash('Tiêu đề và nội dung không được để trống.', 'error')
            return redirect(url_for('main.create_post'))

        # Xử lý upload ảnh
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Tạo tên file duy nhất bằng cách thêm timestamp
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                # Lưu file vào thư mục uploads
                file_path = os.path.join('app/static/uploads', filename)
                file.save(file_path)
                # Lưu đường dẫn tương đối
                image_url = f'/static/uploads/{filename}'

        post = Post(
            title=title,
            content=content,
            source_link=source_link,
            source_content=source_content,
            tags=tags,
            user_id=current_user.id,
            status='approved',  # Bài viết được đăng trực tiếp
            visibility=visibility,
            image_url=image_url
        )

        try:
            db.session.add(post)
            db.session.commit()
            flash('Bài viết đã được đăng thành công.', 'success')
            return redirect(url_for('main.view_post', post_id=post.id))
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi tạo bài viết.', 'error')
    visibility = request.args.get('visibility', 0)
    return render_template('main/create_post.html', visibility=visibility)

@bp.route('/my-posts')
@login_required
def my_posts():
    """Xem danh sách bài viết của mình"""
    if current_user.is_admin():
        flash('Admin không có bài viết cá nhân.', 'error')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=current_user.id)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('main/my_posts.html', posts=posts)

@bp.route('/post/<int:post_id>')
def view_post(post_id):
    """Xem chi tiết bài viết"""
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()
    likes = []
    if current_user.is_authenticated:
        likes = [like.post_id for like in Like.query.filter_by(user_id=current_user.id).all()]
    return render_template('main/view_post.html', post=post, comments=comments, likes=likes)

@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Chỉnh sửa bài viết"""
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != current_user.id:
        flash('Bạn không có quyền chỉnh sửa bài viết này.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.source_link = request.form.get('source_link')
        post.source_content = request.form.get('source_content')
        post.tags = request.form.get('tags')
        post.visibility = request.form.get('visibility')
        post.updated_at = datetime.utcnow()

        # Xử lý upload ảnh mới
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                # Xóa ảnh cũ nếu có
                if post.image_url:
                    old_image_path = os.path.join('app', post.image_url.lstrip('/'))
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                # Lưu ảnh mới
                filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file_path = os.path.join('app/static/uploads', filename)
                file.save(file_path)
                post.image_url = f'/static/uploads/{filename}'
        
        try:
            db.session.commit()
            flash('Bài viết đã được cập nhật thành công.', 'success')
            return redirect(url_for('main.view_post', post_id=post.id))
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi cập nhật bài viết.', 'error')
            
    return render_template('main/edit_post.html', post=post)

@bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Xóa bài viết"""
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != current_user.id:
        flash('Bạn không có quyền xóa bài viết này.', 'error')
        return redirect(url_for('main.index'))

    try:
        db.session.delete(post)
        db.session.commit()
        flash('Bài viết đã được xóa.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra khi xóa bài viết.', 'error')
        
    return redirect(url_for('main.my_posts'))

@bp.route('/post/<int:post_id>/toggle_save', methods=['POST'])
@login_required
def toggle_save_post(post_id):
    post = Post.query.get_or_404(post_id)
    saved_post = SavedPost.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()
    
    if saved_post:
        db.session.delete(saved_post)
        message = 'Đã bỏ lưu bài viết'
        status = 'unsaved'
    else:
        saved_post = SavedPost(user_id=current_user.id, post_id=post_id)
        db.session.add(saved_post)
        message = 'Đã lưu bài viết'
        status = 'saved'
    
    db.session.commit()
    return jsonify({
        'success': True,
        'message': message,
        'status': status
    })

@bp.route('/saved-posts')
@login_required
def saved_posts():
    saved = SavedPost.query.filter_by(user_id=current_user.id)\
        .order_by(SavedPost.saved_at.desc())\
        .all()
    return render_template('main/saved_posts.html', saved_posts=saved) 

@bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    

    if not current_user.is_authenticated:
        flash('Bạn cần đăng nhập để bình luận.', 'warning')
    if request.method == 'POST':  
        content = request.form.get('comment')
        if not content:
            flash('Nội dung bình luận không được để trống.', 'warning')
            return redirect(url_for('main.view_post', post_id=post_id))
        
        comment = Comment(
            content=content,
            user_id=current_user.id,
            post_id=post.id
        )
        try:
            db.session.add(comment)
            db.session.commit()
            flash('Bình luận của bạn đã được đăng.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi đăng bình luận.', 'error')
    
    return redirect(url_for('main.view_post', post_id=post_id))

# chua hoan thanh 
@bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id = current_user.id, post_id = post_id).first()
    if like is None:
        like = Like(
            user_id=current_user.id,
            post_id=post.id
        )
        try:
            db.session.add(like)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Đã thích bài viết',
                'status': 'liked'
            })
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi thích bài viết.', 'error')
    else:
        try:
            db.session.delete(like)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Đã bỏ thích bài viết',
                'status': 'unliked'
            })
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra', 'error')

@bp.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    if current_user.id == user_id:
        return jsonify({
            'success': False,
            'message': 'Bạn không thể follow chính mình'
        })
    
    user_to_follow = User.query.get_or_404(user_id)
    existing_follow = Follow.query.filter_by(
        follower_id=current_user.id,
        followed_id=user_id
    ).first()
    
    if existing_follow:
        return jsonify({
            'success': False,
            'message': 'Bạn đã follow người dùng này'
        })
    
    follow = Follow(follower_id=current_user.id, followed_id=user_id)
    db.session.add(follow)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Đã follow {user_to_follow.username}'
    })

@bp.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow_user(user_id):
    follow = Follow.query.filter_by(
        follower_id=current_user.id,
        followed_id=user_id
    ).first_or_404()
    
    db.session.delete(follow)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Đã unfollow thành công'
    })

@bp.route('/follow')
@login_required
def follow():
    """Hiển thị trang Follow với hai tab: Người theo dõi và Đang theo dõi"""
    active_tab = request.args.get('tab', 'followers')
    
    followers = Follow.query.filter_by(followed_id=current_user.id).all()
    following = Follow.query.filter_by(follower_id=current_user.id).all()
    
    return render_template('main/follow.html',
                         followers=followers,
                         following=following,
                         active_tab=active_tab)

@bp.route('/followers')
@login_required
def followers():
    """Chuyển hướng đến trang Follow với tab Người theo dõi"""
    return redirect(url_for('main.follow', tab='followers'))

@bp.route('/following')
@login_required
def following():
    """Chuyển hướng đến trang Follow với tab Đang theo dõi"""
    return redirect(url_for('main.follow', tab='following'))
