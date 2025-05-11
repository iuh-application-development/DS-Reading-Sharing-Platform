from werkzeug.security import generate_password_hash
from app.models.user import User
from app import db
import os

def create_initial_admin():
    # Kiểm tra xem đã có admin initial chưa
    admin = User.query.filter_by(is_initial_admin=True).first()
    if admin:
        return

    # Tạo admin initial với thông tin từ biến môi trường hoặc mặc định
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')

    admin = User(
        username=admin_username,
        email=admin_email,
        firebase_uid = 'admin1',
        role='admin',
        is_initial_admin=True
    )

    try:
        db.session.add(admin)
        db.session.commit()
        print(f"Initial admin created: {admin_username}")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating initial admin: {str(e)}") 
    pass