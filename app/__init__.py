from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate 
from flask_migrate import Migrate 
from config import Config
import os
from sqlalchemy import inspect

from flask_socketio import SocketIO

socketio = SocketIO()
db = SQLAlchemy()
migrate = Migrate()  
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    socketio.init_app(app)
    UPLOAD_FOLDER = '/tmp/uploads'  # Cloud Run only allows writing to /tmp
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    
    # Đảm bảo thư mục instance tồn tại
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Khởi tạo các extension
    db.init_app(app)
    migrate.init_app(app, db) 
    login_manager.init_app(app)
    
    # Khởi tạo Flask-Migrate
    with app.app_context():
        migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(id):
        from app.models.user import User
        return User.query.get(int(id))

    # Import models
    # Import models
    from app.models.user import User
    from app.models.post import Post
    
    # Đăng ký blueprints
    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.notification import bp as notification_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notification_bp)

    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('users'):
            db.create_all()
        inspector = inspect(db.engine)
        if not inspector.has_table('user'):
            db.create_all()
            from app.utils.admin import create_initial_admin
            create_initial_admin()
            print("Database initialized with initial admin")
        else:
            print("Database already exists, skipping initialization")

    return app

