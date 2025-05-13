FROM python:3.9-slim

WORKDIR /app

# Cài đặt các dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào container
COPY . .

# Tạo thư mục uploads
RUN mkdir -p app/static/uploads

# Expose portL 5000 local - cloud 8080
EXPOSE 5000

# EXPOSE 8080

# Chạy ứng dụng

# dockre
# CMD ["flask", "run", "--host=0.0.0.0"]  local
# cloud
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]