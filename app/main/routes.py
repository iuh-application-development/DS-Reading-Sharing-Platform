@main.route('/search')
def search():
    query = request.args.get('query', '')
    search_type = request.args.get('type', 'all')
    
    if not query:
        return render_template('auth/search.html', 
                             posts=[], 
                             users=[], 
                             hashtags=[],
                             query='',
                             search_type='all')
    
    # Tìm kiếm bài viết
    posts = Post.query.filter(
        or_(
            Post.title.ilike(f'%{query}%'),
            Post.content.ilike(f'%{query}%')
        )
    ).all() if search_type in ['all', 'posts'] else []
    
    # Tìm kiếm người dùng
    users = User.query.filter(
        or_(
            User.username.ilike(f'%{query}%'),
            User.email.ilike(f'%{query}%')
        )
    ).all() if search_type in ['all', 'users'] else []
    
    # Tìm kiếm hashtag
    hashtag_query = query.lstrip('#') if query.startswith('#') else query
    hashtags = Post.query.filter(
        Post.hashtags.ilike(f'%{hashtag_query}%')
    ).all() if search_type in ['all', 'hashtags'] else []
    
    return render_template('auth/search.html',
                         posts=posts,
                         users=users,
                         hashtags=hashtags,
                         query=query,
                         search_type=search_type)

@main.route('/notifications')
@login_required
def notifications():
    # Lấy danh sách thông báo của người dùng hiện tại
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).all()
    
    return render_template('auth/notifications.html', notifications=notifications) 