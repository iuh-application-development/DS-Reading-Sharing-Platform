import pytest
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user
from flask_testing import TestCase
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from app.models.saved_post import SavedPost
from app.models.post import Post
from app.models.like import Like
from app.models.comment import Comment
from app.models.notification import Notification
from app.models.follow import Follow
from datetime import datetime
from unittest.mock import patch, MagicMock
from werkzeug.utils import secure_filename
from firebase_admin import auth
from app.utils.time_vn import vn_now
from io import BytesIO

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'Uploads')
    WTF_CSRF_ENABLED = False  # Tắt CSRF để đơn giản hóa kiểm thử

@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY='test-secret-key',
        UPLOAD_FOLDER=os.path.join(os.path.dirname(__file__), 'static', 'Uploads'),
        WTF_CSRF_ENABLED=False
    )
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_user(app):
    with app.app_context():
        user = User(
            firebase_uid='test_uid',
            username='testuser',
            email='test@example.com',
            full_name='Test User',
            avatar_url=None,  # Không cần is_active
            role='user',
            created_at=vn_now()
        )
        db.session.add(user)
        db.session.commit()
        yield user

@pytest.fixture
def init_post(app, init_user):
    with app.app_context():
        post = Post(
            title="Test Post",
            content="Test Content",
            user_id=init_user.id,
            status='approved',
            created_at=vn_now()
        )
        db.session.add(post)
        db.session.commit()
        yield post

@pytest.fixture
def init_admin(app):
    with app.app_context():
        admin = User(
            firebase_uid='admin_uid',
            username='admin',
            email='admin@example.com',
            full_name='Admin User',
            role='admin',
            is_initial_admin=True,
            created_at=vn_now()
        )
        db.session.add(admin)
        db.session.commit()
        yield admin

# Unit Tests cho User model
def test_user_is_admin(app, init_user):
    with app.app_context():
        assert init_user.is_admin() == False
        init_user.role = 'admin'
        db.session.commit()
        assert init_user.is_admin() == True

def test_user_can_manage_users(app, init_user):
    with app.app_context():
        assert init_user.can_manage_users() == False
        init_user.role = 'admin'
        init_user.is_initial_admin = True
        db.session.commit()
        assert init_user.can_manage_users() == True

def test_generate_avatar_seed(app, init_user):
    with app.app_context():
        seed = init_user.generate_avatar_seed()
        assert isinstance(seed, str)
        assert len(seed) == 32  # MD5 hash length

from app.models.post import Post

def test_has_saved_post(app, init_user):
    with app.app_context():
        # Tạo bài viết giả
        post = Post(id=1, user_id=init_user.id, title="Test", content="Hello", status='approved')
        db.session.add(post)
        db.session.commit()

        saved_post = SavedPost(user_id=init_user.id, post_id=post.id)
        db.session.add(saved_post)
        db.session.commit()

        assert init_user.has_saved_post(post.id) is True
        assert init_user.has_saved_post(999) is False

@patch('app.models.user.User.get_avatar_path')
def test_get_avatar_path_with_filename(mock_get_avatar_path, app, init_user):
    mock_get_avatar_path.return_value = 'uploads/avatars/test_avatar.jpg'
    with app.app_context():
        assert init_user.get_avatar_path() == 'uploads/avatars/test_avatar.jpg'


def test_get_avatar_path_with_url(app, init_user):
    with app.app_context():
        init_user.avatar_filename = None
        init_user.avatar_url = 'https://gravatar.com/test'
        db.session.commit()
        avatar_path = init_user.get_avatar_path()
        assert avatar_path == 'https://gravatar.com/test'

def test_generate_random_avatar(app):
    with app.app_context():
        avatar_url = User.generate_random_avatar()
        assert avatar_url.startswith('https://www.gravatar.com/avatar/')
        assert 'd=identicon' in avatar_url

# Integration Tests cho Auth routes
@patch('firebase_admin.auth.verify_id_token')
@patch('firebase_admin.auth.get_user')
def test_firebase_login_success(mock_get_user, mock_verify, app, client, init_user):
    mock_verify.return_value = {'uid': 'test_uid', 'email': 'test@example.com'}
    mock_get_user.return_value = MagicMock(disabled=False)

    response = client.post(
        '/firebase-login',
        json={'status': 'success', 'message': ''},
        headers={'Authorization': 'Bearer test_token'}
    )

    assert response.status_code == 200
    assert response.json['redirect'] == '/'


def test_firebase_login_invalid_token(app, client):
    with app.app_context():
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.side_effect = auth.InvalidIdTokenError('Invalid token')
            response = client.post(
                '/firebase-login',
                json={'status': 'success', 'message': ''},
                headers={'Authorization': 'Bearer invalid_token'}
            )
            assert response.status_code == 401
            assert response.json['redirect'] == '/login'
            with client.session_transaction() as sess:
                flashes = sess.get('_flashes', [])
                assert any('Token không hợp lệ' in msg for msg, _ in flashes)

def test_firebase_register_success(app, client):
    with app.app_context():
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.return_value = {'uid': 'new_uid', 'email': 'newuser@example.com'}
            response = client.post(
                '/firebase-register',
                json={
                    'status': 'success',
                    'idToken': 'new_token',
                    'first_name': 'New',
                    'last_name': 'User',
                    'message': ''
                }
            )
            assert response.status_code == 200
            assert response.json['redirect'] == '/login'
            user = User.query.filter_by(email='newuser@example.com').first()
            assert user is not None
            assert user.username == 'newuser'
            assert user.full_name == 'User New'

def test_logout(app, client, init_user):
    with app.app_context():
        with client:
            # Tạo yêu cầu giả lập để thiết lập session
            client.get('/')
            login_user(init_user)
            response = client.get('/logout')
            assert response.status_code == 302
            assert response.location.endswith('/')

from io import BytesIO

def test_upload_avatar_success(app, client, init_user):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            image_data = BytesIO(b'test image data')
            image_data.name = 'test.jpg'

            response = client.post(
                '/upload-avatar',
                data={'avatar': (image_data, 'test.jpg')},
                content_type='multipart/form-data'
            )

            assert response.status_code == 302

def test_edit_profile_success(app, client, init_user):
    with app.app_context():
        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(init_user.id)

            response = client.post(
                '/edit_profile',
                data={
                    'full_name': 'Updated Name',
                    'phone': '1234567890',
                    'date_of_birth': '2000-01-01',
                    'gender': 'male',
                    'bio': 'Updated bio'
                }
            )

            assert response.status_code == 302
            user = User.query.get(init_user.id)
            assert user.full_name == 'Updated Name'

# Additional fixtures
@pytest.fixture
def init_post(app, init_user):
    with app.app_context():
        post = Post(
            title="Test Post",
            content="Test Content",
            user_id=init_user.id,
            status='approved',
            created_at=vn_now()
        )
        db.session.add(post)
        db.session.commit()
        yield post

@pytest.fixture
def init_admin(app):
    with app.app_context():
        admin = User(
            firebase_uid='admin_uid',
            username='admin',
            email='admin@example.com',
            full_name='Admin User',
            role='admin',
            is_initial_admin=True,
            created_at=vn_now()
        )
        db.session.add(admin)
        db.session.commit()
        yield admin

# Auth Tests
def test_firebase_login_success(app, client, init_user):
    with patch('firebase_admin.auth.verify_id_token') as mock_verify:
        mock_verify.return_value = {'uid': 'test_uid', 'email': 'test@example.com'}
        response = client.post(
            '/firebase-login',
            json={'status': 'success', 'message': ''},
            headers={'Authorization': 'Bearer test_token'}
        )
        assert response.status_code == 200
        assert response.json['redirect'] == '/'

def test_firebase_register_success(app, client):
    with patch('firebase_admin.auth.verify_id_token') as mock_verify:
        mock_verify.return_value = {'uid': 'new_uid', 'email': 'newuser@example.com'}
        response = client.post(
            '/firebase-register',
            json={
                'status': 'success',
                'idToken': 'new_token',
                'first_name': 'New',
                'last_name': 'User',
                'message': ''
            }
        )
        assert response.status_code == 200
        assert response.json['redirect'] == '/login'
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.username == 'newuser'

def test_upload_avatar_success(app, client, init_user):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            image_data = BytesIO(b'test image data')
            image_data.name = 'test.jpg'
            response = client.post(
                '/upload-avatar',
                data={'avatar': (image_data, 'test.jpg')},
                content_type='multipart/form-data'
            )
            assert response.status_code == 302

def test_search_posts(app, client, init_user, init_post):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            response = client.get('/search?query=Test&search_type=all')
            assert response.status_code == 200
            assert b'Test Post' in response.data

# Main Tests
def test_create_post(app, client, init_user):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            response = client.post(
                '/create_post',
                data={
                    'title': 'New Post',
                    'content': 'Post Content',
                    'visibility': '0'
                }
            )
            assert response.status_code == 302
            post = Post.query.filter_by(title='New Post').first()
            assert post is not None

def test_toggle_like(app, client, init_user, init_post):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            response = client.post(f'/post/{init_post.id}/like')
            assert response.status_code == 200
            assert response.json['success'] is True
            like = Like.query.filter_by(user_id=init_user.id, post_id=init_post.id).first()
            assert like is not None

def test_toggle_save_post(app, client, init_user, init_post):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            response = client.post(f'/post/{init_post.id}/toggle_save')
            assert response.status_code == 200
            assert response.json['success'] is True
            saved = SavedPost.query.filter_by(user_id=init_user.id, post_id=init_post.id).first()
            assert saved is not None

def test_add_comment(app, client, init_user, init_post):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            response = client.post(
                f'/post/{init_post.id}/comment',
                data={'comment': 'Test comment'}
            )
            assert response.status_code == 302
            comment = Comment.query.filter_by(post_id=init_post.id).first()
            assert comment is not None
            assert comment.content == 'Test comment'

def test_follow_user(app, client, init_user):
    with app.app_context():
        # Create another user to follow
        other_user = User(
            firebase_uid='other_uid',
            username='otheruser',
            email='other@example.com',
            created_at=vn_now()
        )
        db.session.add(other_user)
        db.session.commit()
        
        with client:
            client.get('/')
            login_user(init_user)
            response = client.post(f'/follow/{other_user.id}')
            assert response.status_code == 200
            assert response.json['success'] is True
            follow = Follow.query.filter_by(follower_id=init_user.id, followed_id=other_user.id).first()
            assert follow is not None

# Admin Tests
def test_admin_dashboard(app, client, init_admin):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_admin)
            response = client.get('/admin/dashboard')
            assert response.status_code == 200
            assert b'Dashboard' in response.data

def test_manage_users(app, client, init_admin, init_user):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_admin)
            response = client.get('/admin/users')
            assert response.status_code == 200
            assert b'Manage Users' in response.data

def test_toggle_user_status(app, client, init_admin, init_user):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_admin)
            response = client.post(
                f'/admin/user/{init_user.id}/toggle_status',
                data={'status': 'banned'}
            )
            assert response.status_code == 302

def test_review_post(app, client, init_admin, init_post):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_admin)
            response = client.post(
                f'/admin/post/{init_post.id}/review',
                data={'action': 'approve'}
            )
            assert response.status_code == 302
            post = Post.query.get(init_post.id)
            assert post.status == 'approved'

# Notification Tests
def test_get_notifications(app, client, init_user):
    with app.app_context():
        # Create a test notification
        notification = Notification(
            user_id=init_user.id,
            post_id=1,
            message='Test notification',
            type='test',
            created_at=vn_now()
        )
        db.session.add(notification)
        db.session.commit()
        
        with client:
            client.get('/')
            login_user(init_user)
            response = client.get('/notifications')
            assert response.status_code == 200
            assert b'Test notification' in response.data

def test_mark_notification_read(app, client, init_user):
    with app.app_context():
        # Create a test notification
        notification = Notification(
            user_id=init_user.id,
            post_id=1,
            message='Test notification',
            type='test',
            created_at=vn_now()
        )
        db.session.add(notification)
        db.session.commit()
        
        with client:
            client.get('/')
            login_user(init_user)
            response = client.post(f'/notifications/{notification.id}/mark-read')
            assert response.status_code == 200
            assert response.json['success'] is True
            notification = Notification.query.get(notification.id)
            assert notification.is_read is True

def test_mark_all_notifications_read(app, client, init_user):
    with app.app_context():
        # Create multiple test notifications
        for i in range(3):
            notification = Notification(
                user_id=init_user.id,
                post_id=i,
                message=f'Test notification {i}',
                type='test',
                created_at=vn_now()
            )
            db.session.add(notification)
        db.session.commit()
        
        with client:
            client.get('/')
            login_user(init_user)
            response = client.post('/notifications/mark-all-read')
            assert response.status_code == 200
            assert response.json['success'] is True
            notifications = Notification.query.filter_by(user_id=init_user.id).all()
            assert all(n.is_read for n in notifications)
