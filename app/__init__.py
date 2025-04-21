from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os
from sqlalchemy import inspect  # Import inspect từ sqlalchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Đảm bảo thư mục instance tồn tại
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        from app.models.user import User
        return User.query.get(int(id))

    # Import các models
    from app.models.user import User
    from app.models.post import Post
    
    # Đăng ký blueprints
    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.admin import bp as admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    # Chỉ tạo database và admin nếu cần
    with app.app_context():
        # Kiểm tra xem bảng đã tồn tại chưa
        inspector = inspect(db.engine)  # Sử dụng inspect từ sqlalchemy
        if not inspector.has_table('user'):  # Kiểm tra bảng 'user'
            db.create_all()  # Tạo database nếu chưa tồn tại
            from app.utils.admin import create_initial_admin
            create_initial_admin()
            print("Database initialized with initial admin")
        else:
            print("Database already exists, skipping initialization")

    return app