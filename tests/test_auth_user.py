import pytest
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user
from flask_testing import TestCase
from app import create_app, db
from app.models.user import User
from app.models.saved_post import SavedPost
from datetime import datetime
from unittest.mock import patch, MagicMock
import os
from werkzeug.utils import secure_filename
from firebase_admin import auth
from app.utils.time_vn import vn_now

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
            avatar_url=None,  # Đặt avatar_url là None để kiểm tra avatar_filename
            is_active=True,
            role='user',
            created_at=vn_now
        )
        db.session.add(user)
        db.session.commit()
        yield user

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

def test_has_saved_post(app, init_user):
    with app.app_context():
        saved_post = SavedPost(user_id=init_user.id, post_id=1)
        db.session.add(saved_post)
        db.session.commit()
        assert init_user.has_saved_post(1) == True
        assert init_user.has_saved_post(2) == False

def test_get_avatar_path_with_filename(app, init_user):
    with app.app_context():
        init_user.avatar_filename = 'test_avatar.jpg'
        init_user.avatar_url = None  # Đảm bảo avatar_url không can thiệp
        db.session.commit()
        with patch('os.path.exists', return_value=True):  # Giả lập tệp tồn tại
            avatar_path = init_user.get_avatar_path()
            assert avatar_path == 'uploads/avatars/test_avatar.jpg'

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
def test_firebase_login_success(app, client, init_user):
    with app.app_context():
        with patch('firebase_admin.auth.verify_id_token') as mock_verify:
            mock_verify.return_value = {'uid': 'test_uid', 'email': 'test@example.com'}
            response = client.post(
                '/firebase-login',
                json={'status': 'success', 'message': ''},
                headers={'Authorization': 'Bearer test_token'}
            )
            assert response.status_code == 200
            assert response.json['redirect'] == '/'
            with client.session_transaction() as sess:
                flashes = sess.get('_flashes', [])
                assert any('Đăng nhập thành công' in msg for msg, _ in flashes)

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

def test_upload_avatar_success(app, client, init_user):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), exist_ok=True)
            with patch('os.path.exists', return_value=True):
                response = client.post(
                    '/upload-avatar',
                    data={'avatar': (open('test.jpg', 'rb'), 'test.jpg')},
                    content_type='multipart/form-data'
                )
                assert response.status_code == 302
                assert response.location.endswith(f'/profile/{init_user.username}')
                user = User.query.get(init_user.id)
                assert user.avatar_filename is not None
                assert user.avatar_filename.endswith('.jpg')

def test_edit_profile_success(app, client, init_user):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
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
            assert response.location.endswith(f'/profile/{init_user.username}')
            user = User.query.get(init_user.id)
            assert user.full_name == 'Updated Name'
            assert user.phone == '1234567890'
            assert user.gender == 'male'
            assert user.bio == 'Updated bio'