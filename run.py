from app import create_app
import os
from app.routes.notification import bp as notification_bp

# Đảm bảo thư mục instance tồn tại trước khi tạo app
os.makedirs('instance', exist_ok=True)

app = create_app()
app.register_blueprint(notification_bp)

if __name__ == '__main__':
    app.run(debug=True) 