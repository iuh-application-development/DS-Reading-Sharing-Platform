from app import create_app, socketio
import os
import logging

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Đảm bảo thư mục instance tồn tại trước khi tạo app
os.makedirs('instance', exist_ok=True)

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)
