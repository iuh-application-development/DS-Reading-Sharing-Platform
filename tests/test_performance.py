import pytest
import time
from io import BytesIO
from unittest.mock import patch, MagicMock
from flask_login import login_user
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from app.models.post import Post
from app.models.saved_post import SavedPost
from app.models.notification import Notification
from app.utils.time_vn import vn_now


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'Uploads')


@pytest.fixture
def app():
    app = create_app()
    app.config.from_object(TestConfig)
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
            avatar_url=None,
            role='user',
            created_at=vn_now()
        )
        db.session.add(user)
        db.session.commit()
        yield user


# ========== Performance Tests ==========

def test_response_time_login(app, client, init_user):
    with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
         patch('firebase_admin.auth.get_user') as mock_get_user:
        mock_verify.return_value = {'uid': 'test_uid', 'email': 'test@example.com'}
        mock_get_user.return_value = MagicMock(disabled=False)

        start = time.time()
        response = client.post(
            '/firebase-login',
            json={'status': 'success', 'message': ''},
            headers={'Authorization': 'Bearer test_token'}
        )
        duration = time.time() - start

        print(f"firebase-login time: {duration:.4f}s")
        assert response.status_code == 200
        assert duration < 3  # cho phép lên đến 3 giây


def test_response_time_edit_profile(app, client, init_user):
    with app.app_context():
        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(init_user.id)

            start = time.time()
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
            duration = time.time() - start
            print(f"edit_profile time: {duration:.4f}s")
            assert response.status_code == 302
            assert duration < 3


def test_response_time_upload_avatar(app, client, init_user):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            image_data = BytesIO(b'test image data')
            image_data.name = 'test.jpg'

            start = time.time()
            response = client.post(
                '/upload-avatar',
                data={'avatar': (image_data, 'test.jpg')},
                content_type='multipart/form-data'
            )
            duration = time.time() - start
            print(f"upload-avatar time: {duration:.4f}s")
            assert response.status_code == 302
            assert duration < 3


# ========== Benchmark Tests ==========

def test_benchmark_login(benchmark, client, init_user):
    with patch('firebase_admin.auth.verify_id_token') as mock_verify, \
         patch('firebase_admin.auth.get_user') as mock_get_user:
        mock_verify.return_value = {'uid': 'test_uid', 'email': 'test@example.com'}
        mock_get_user.return_value = MagicMock(disabled=False)

        def perform_request():
            return client.post(
                '/firebase-login',
                json={'status': 'success', 'message': ''},
                headers={'Authorization': 'Bearer test_token'}
            )

        result = benchmark(perform_request)
        assert result.status_code == 200


def test_benchmark_edit_profile(benchmark, app, client, init_user):
    with app.app_context():
        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(init_user.id)

            def perform_edit():
                return client.post(
                    '/edit_profile',
                    data={
                        'full_name': 'Updated Name',
                        'phone': '1234567890',
                        'date_of_birth': '2000-01-01',
                        'gender': 'male',
                        'bio': 'Updated bio'
                    }
                )

            result = benchmark(perform_edit)
            assert result.status_code == 302


def test_benchmark_upload_avatar(benchmark, app, client, init_user):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)

            def upload():
                image_data = BytesIO(b'test image data')  # tạo mới mỗi lần benchmark
                image_data.name = 'test.jpg'
                return client.post(
                    '/upload-avatar',
                    data={'avatar': (image_data, 'test.jpg')},
                    content_type='multipart/form-data'
                )

            result = benchmark(upload)
            assert result.status_code == 302


# Post Operations Performance Tests
def test_response_time_create_post(app, client, init_user):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            
            start = time.time()
            response = client.post(
                '/create_post',
                data={
                    'title': 'Performance Test Post',
                    'content': 'Test content for performance testing',
                    'visibility': '0'
                }
            )
            duration = time.time() - start
            
            print(f"create_post time: {duration:.4f}s")
            assert response.status_code == 302
            assert duration < 3

def test_response_time_load_feed(app, client, init_user):
    with app.app_context():
        # Create some test posts
        for i in range(10):
            post = Post(
                title=f"Test Post {i}",
                content=f"Content {i}",
                user_id=init_user.id,
                status='approved',
                created_at=vn_now()
            )
            db.session.add(post)
        db.session.commit()
        
        with client:
            client.get('/')
            login_user(init_user)
            
            start = time.time()
            response = client.get('/')
            duration = time.time() - start
            
            print(f"Feed load time: {duration:.4f}s")
            assert response.status_code == 200
            assert duration < 3

def test_response_time_search_posts(app, client, init_user):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            
            start = time.time()
            response = client.get('/search?query=test&search_type=all')
            duration = time.time() - start
            
            print(f"Search time: {duration:.4f}s")
            assert response.status_code == 200
            assert duration < 3

# Social Interactions Performance Tests
def test_response_time_like_post(app, client, init_user, init_post):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            
            start = time.time()
            response = client.post(f'/post/{init_post.id}/like')
            duration = time.time() - start
            
            print(f"Like post time: {duration:.4f}s")
            assert response.status_code == 200
            assert duration < 3

def test_response_time_comment_post(app, client, init_user, init_post):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            
            start = time.time()
            response = client.post(
                f'/post/{init_post.id}/comment',
                data={'comment': 'Performance test comment'}
            )
            duration = time.time() - start
            
            print(f"Comment time: {duration:.4f}s")
            assert response.status_code == 302
            assert duration < 3

def test_response_time_follow_user(app, client, init_user):
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
            
            start = time.time()
            response = client.post(f'/follow/{other_user.id}')
            duration = time.time() - start
            
            print(f"👥 Follow user time: {duration:.4f}s")
            assert response.status_code == 200
            assert duration < 3

# Notification Performance Tests
def test_response_time_create_notification(app, client, init_user, init_post):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            
            start = time.time()
            response = client.post(
                f'/post/{init_post.id}/like'  # This will trigger a notification
            )
            duration = time.time() - start
            
            print(f"Create notification time: {duration:.4f}s")
            assert response.status_code == 200
            assert duration < 3

def test_response_time_get_notifications(app, client, init_user):
    with app.app_context():
        # Create multiple test notifications
        for i in range(20):  # Create more notifications to test pagination
            notification = Notification(
                user_id=init_user.id,
                post_id=1,
                message=f'Test notification {i}',
                type='like',
                created_at=vn_now()
            )
            db.session.add(notification)
        db.session.commit()
        
        with client:
            client.get('/')
            login_user(init_user)
            
            start = time.time()
            response = client.get('/notifications')
            duration = time.time() - start
            
            print(f"Get notifications time: {duration:.4f}s")
            assert response.status_code == 200
            assert duration < 3

def test_response_time_get_unread_count(app, client, init_user):
    with app.app_context():
        # Create mix of read and unread notifications
        for i in range(15):
            notification = Notification(
                user_id=init_user.id,
                post_id=1,
                message=f'Test notification {i}',
                type='like',
                is_read=(i % 2 == 0),  # Alternate between read and unread
                created_at=vn_now()
            )
            db.session.add(notification)
        db.session.commit()
        
        with client:
            client.get('/')
            login_user(init_user)
            
            start = time.time()
            response = client.get('/notifications/unread-count')
            duration = time.time() - start
            
            print(f"Get unread count time: {duration:.4f}s")
            assert response.status_code == 200
            assert duration < 3

def test_response_time_mark_all_read(app, client, init_user):
    with app.app_context():
        # Create multiple unread notifications
        for i in range(20):
            notification = Notification(
                user_id=init_user.id,
                post_id=1,
                message=f'Test notification {i}',
                type='like',
                is_read=False,
                created_at=vn_now()
            )
            db.session.add(notification)
        db.session.commit()
        
        with client:
            client.get('/')
            login_user(init_user)
            
            start = time.time()
            response = client.post('/notifications/mark-all-read')
            duration = time.time() - start
            
            print(f"Mark all as read time: {duration:.4f}s")
            assert response.status_code == 200
            assert duration < 3

def test_response_time_mark_single_read(app, client, init_user):
    with app.app_context():
        # Create a test notification
        notification = Notification(
            user_id=init_user.id,
            post_id=1,
            message='Test notification',
            type='like',
            is_read=False,
            created_at=vn_now()
        )
        db.session.add(notification)
        db.session.commit()
        
        with client:
            client.get('/')
            login_user(init_user)
            
            start = time.time()
            response = client.post(f'/notifications/{notification.id}/mark-read')
            duration = time.time() - start
            
            print(f"Mark single as read time: {duration:.4f}s")
            assert response.status_code == 200
            assert duration < 3

# Benchmark Tests for Notifications
def test_benchmark_get_notifications(benchmark, app, client, init_user):
    with app.app_context():
        # Create test notifications
        for i in range(20):
            notification = Notification(
                user_id=init_user.id,
                post_id=1,
                message=f'Test notification {i}',
                type='like',
                created_at=vn_now()
            )
            db.session.add(notification)
        db.session.commit()
        
        with client:
            client.get('/')
            login_user(init_user)
            
            def get_notifications():
                return client.get('/notifications')
            
            result = benchmark(get_notifications)
            assert result.status_code == 200

def test_benchmark_mark_all_read(benchmark, app, client, init_user):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            
            def mark_all_read():
                return client.post('/notifications/mark-all-read')
            
            result = benchmark(mark_all_read)
            assert result.status_code == 200

def test_benchmark_get_unread_count(benchmark, app, client, init_user):
    with app.app_context():
        with client:
            client.get('/')
            login_user(init_user)
            
            def get_unread_count():
                return client.get('/notifications/unread-count')
            
            result = benchmark(get_unread_count)
            assert result.status_code == 200
