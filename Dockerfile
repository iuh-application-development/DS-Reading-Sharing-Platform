FROM python:3.9-slim

WORKDIR /app

# Cài đặt các dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào container
COPY . .
COPY firebase-auth.json /app/firebase-auth.json

# Tạo thư mục uploads
#docker
# RUN mkdir -p app/static/uploads

#cloud
RUN mkdir -p /tmp/uploads

ENV FLASK_APP=run.py

# Expose portL 5000 local - cloud 8080
# EXPOSE 5000

EXPOSE 8080

# Chạy ứng dụng
# docker
# CMD ["flask", "run", "--host=0.0.0.0"]  


# cloud
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]

