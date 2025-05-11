FROM python:3.9-slim

WORKDIR /app

# Cài đặt các dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào container
COPY . .

# Tạo thư mục uploads
RUN mkdir -p app/static/uploads

# Expose port 5000
EXPOSE 5000

# Chạy ứng dụng
CMD ["flask", "run", "--host=0.0.0.0"] 