import os
import firebase_admin
from firebase_admin import auth, credentials
from app import db
from app.models.user import User

def create_initial_admin():
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase-auth.json")  
        firebase_admin.initialize_app(cred)

    admin_email = os.environ.get("ADMIN_EMAIL", "admin@admin.admin")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")

    try:
        user_record = auth.get_user_by_email(admin_email)
        firebase_uid = user_record.uid
    except auth.UserNotFoundError:
        # tạo mới tài khoản
        user_record = auth.create_user(
            email=admin_email,
            password=admin_password,
            display_name="Admin"
        )
        print("🆕 Admin account created on Firebase.")
        firebase_uid = user_record.uid

    # Kiểm tra trong DB Flask xem đã có chưa
    if User.query.filter_by(firebase_uid=firebase_uid).first():
        return

    # Tạo user admin trong local database
    admin_user = User(
        username="admin",
        email=admin_email,
        firebase_uid=firebase_uid,
        role="admin",
        is_initial_admin=True
    )

    try:
        db.session.add(admin_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Khoi tao admin that bai: {e}")
