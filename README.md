# **Đặc tả dự án DS-Reading-Platform**

## **1. Mô tả chung**

**DS-Reading-Platform** là một nền tảng web giúp người dùng đăng bài, chia sẻ bài viết với nội dung phong phú từ nhiều nguồn. Người dùng có thể:

* Đính kèm **link bài viết** hoặc **nội dung text** vào khung bên trái.
* Soạn bài post của riêng mình ở khung bên phải, có thể viết nhận xét, phân tích hoặc chia sẻ quan điểm.
* Chia sẻ bài đăng của họ với cộng đồng.

Hệ thống có cơ chế **quản trị viên (admin)** để giám sát nội dung và quản lý người dùng.

## **2. Công nghệ sử dụng**

* **Backend** : Flask
* **Frontend** : Flask, Tailwindcss và React.js cho giao diện
* **Cơ sở dữ liệu** : SQLite
* **Môi trường ảo hóa** : Máy ảo (VM) để đảm bảo tính độc lập và hiệu suất cao (python -m venv venv)

---

## **3. Chức năng chính**

### **3.1. Chức năng dành cho user**

✅ **Đăng ký, đăng nhập, đăng xuất**

✅ **Đăng bài** :

* Nhập **link hoặc nội dung bài viết gốc** vào khung bên trái.
* Soạn bài viết của riêng mình ở khung bên phải.
* Có thể thêm tiêu đề, tag, định dạng markdown cơ bản.

✅ **Tương tác với bài viết** :

* Like, bình luận, lưu bài viết.
* Chia sẻ bài viết của người khác.

✅ **Quản lý bài viết cá nhân** :

* Xem danh sách bài đã đăng.
* Chỉnh sửa hoặc xóa bài viết của mình.

✅ **Tìm kiếm bài viết** :

* Lọc bài theo tag hoặc từ khóa.

✅ **Quản lý follow** :

* Theo dõi người dùng khác.
* Xem danh sách người đang theo dõi và người theo dõi mình.
* Nhận thông báo khi người theo dõi đăng bài mới.

✅ **Đăng bài với hình ảnh** :

* Đính kèm hình ảnh khi đăng bài.
* Hỗ trợ nhiều định dạng ảnh (JPG, PNG, GIF).
* Tự động resize ảnh để tối ưu hiệu suất.

---

### **3.2. Chức năng dành cho admin**

✅ **Quản lý user**

* Xem danh sách user.
* Chặn/tắt tài khoản vi phạm.

✅ **Duyệt bài viết**

* Kiểm duyệt nội dung bài viết nếu cần.
* Ẩn hoặc xóa bài nếu vi phạm.

✅ **Phân quyền admin**

* **Admin initial** :
  * Là admin đầu tiên được tạo khi khởi tạo database.
  * Không hiển thị trong danh sách user, không user nào có quyền thấy nó.
  * Có quyền quản lý user khác, đóng/ngắt hoạt động, vô hiệu hóa và kích hoạt user khác.
  * Ban đầu, chỉ có duy nhất admin initial, không có admin cấp dưới.

---

## **4. Cấu trúc database (SQLite)**

### **4.1. Bảng `users` (quản lý người dùng)**

| user_id  | username | email | password_hash | role              | created_at |
| -------- | -------- | ----- | ------------- | ----------------- | ---------- |
| INT (PK) | TEXT     | TEXT  | TEXT          | TEXT (user/admin) | TIMESTAMP  |

### **4.2. Bảng `posts` (quản lý bài viết)**

| post_id  | user_id (FK) | title | content | source_link | tags | image_url | created_at |
| -------- | ------------ | ----- | ------- | ----------- | ---- | --------- | ---------- |
| INT (PK) | INT          | TEXT  | TEXT    | TEXT        | TEXT | TEXT      | TIMESTAMP  |

### **4.3. Bảng `comments` (bình luận bài viết)**

| comment_id | post_id (FK) | user_id (FK) | content | created_at |
| ---------- | ------------ | ------------ | ------- | ---------- |
| INT (PK)   | INT          | INT          | TEXT    | TIMESTAMP  |

### **4.4. Bảng `likes` (lượt thích)**

| like_id  | post_id (FK) | user_id (FK) | created_at |
| -------- | ------------ | ------------ | ---------- |
| INT (PK) | INT          | INT          | TIMESTAMP  |

### **4.5. Bảng `follows` (quản lý follow)**

| follow_id | follower_id (FK) | followed_id (FK) | created_at |
| --------- | ---------------- | ---------------- | ---------- |
| INT (PK)  | INT              | INT              | TIMESTAMP  |

* `follower_id`: ID của người theo dõi
* `followed_id`: ID của người được theo dõi
* Mỗi cặp follower_id và followed_id là duy nhất

### **4.6. Bảng `images` (quản lý hình ảnh)**

| image_id  | post_id (FK) | filename | file_path | created_at |
| --------- | ------------ | -------- | --------- | ---------- |
| INT (PK)  | INT          | TEXT     | TEXT      | TIMESTAMP  |

* `filename`: Tên file gốc
* `file_path`: Đường dẫn lưu trữ file
* Mỗi bài viết có thể có nhiều hình ảnh

---

## **5. Quy trình hoạt động**

### **5.1. Khởi tạo hệ thống**

1️⃣ Tạo cơ sở dữ liệu SQLite.

2️⃣ Thêm **admin initial** vào database.

3️⃣ Admin initial có toàn quyền quản lý user và bài viết, không xuất hiện trong danh sách user thông thường.

### **5.2. Quy trình đăng bài**

1️⃣ User nhập link bài viết gốc hoặc nội dung gốc vào khung bên trái.

2️⃣ User viết bài post của mình bên phải.

3️⃣ User nhấn  **Đăng bài** , bài viết sẽ được lưu vào database.

### **5.3. Quy trình phân quyền admin**

* Ban đầu chỉ có admin initial.
* Admin initial có thể cấp quyền admin cho user khác nếu cần.
* Admin cấp dưới không thể xóa hoặc thay đổi admin initial.

---

## **6. Hạ tầng triển khai**

* **Máy ảo (VM)** : Tạo môi trường độc lập, tránh xung đột với hệ thống khác.

## **7. Cây thư mục:**

ds-reading-platform/<br>
├── .env                    # Chứa biến môi trường<br>
├── .gitignore             # Cấu hình git ignore<br>
├── requirements.txt       # Danh sách package cần thiết<br>
├── run.py                # File chạy ứng dụng<br>
├── config.py             # Cấu hình ứng dụng<br>
│<br>
├── app/<br>
│   ├── __init__.py       # Khởi tạo ứng dụng Flask<br>
│   │<br>
│   ├── models/           # Các model database<br>
│   │   ├── __init__.py<br>
│   │   ├── user.py      # Model User<br>
│   │   ├── post.py      # Model Post<br>
│   │   ├── comment.py   # Model Comment<br>
│   │   └── like.py      # Model Like<br>
│   │<br>
│   ├── routes/          # Các route của ứng dụng<br>
│   │   ├── __init__.py<br>
│   │   ├── auth.py      # Route xác thực<br>
│   │   ├── main.py      # Route chính<br>
│   │   └── admin.py     # Route admin<br>
│   │<br>
│   ├── templates/       # Templates HTML<br>
│   │   ├── base.html    # Template cơ sở<br>
│   │   ├── auth/<br>
│   │   │   ├── login.html<br>
│   │   │   └── register.html<br>
│   │   ├── main/<br>
│   │   │   ├── index.html<br>
│   │   │   ├── create_post.html<br>
│   │   │   └── view_post.html<br>
│   │   └── admin/<br>
│   │       ├── dashboard.html<br>
│   │       ├── users.html<br>
│   │       └── posts.html<br>
│   │<br>
│   ├── static/         # File tĩnh<br>
│   │   ├── css/<br>
│   │   │   └── main.css<br>
│   │   ├── js/<br>
│   │   │   └── main.js<br>
│   │   └── img/<br>
│   │<br>
│   └── utils/         # Các hàm tiện ích<br>
│       ├── __init__.py<br>
│       └── decorators.py<br>
│<br>
├── tests/            # Unit tests<br>
│   ├── __init__.py<br>
│   ├── test_auth.py<br>
│   └── test_posts.py<br>
│<br>
└── venv/            # Môi trường ảo Python (sẽ được tạo sau)

## **8. Hướng dẫn cài đặt và sử dụng**

### **8.1. Yêu cầu hệ thống**
* Docker Desktop
* Git
* pgAdmin (tùy chọn - để quản lý database)

### **8.2. Các bước cài đặt**

1️⃣ **Clone repository**
```bash
git clone https://github.com/iuh-application-development/DS-Reading-Sharing-Platform.git
cd DS-Reading-Sharing-Platform
```

<!-- 2️⃣ **Tạo file .env**
```bash
cp .env.example .env
``` -->
tôi đã cấu hình không loại bỏ .env nên không cần làm bước này

3️⃣ **Khởi động ứng dụng với Docker**
```bash
docker-compose up --build
```

4️⃣ **Truy cập ứng dụng**
* Web: http://localhost:5001
* Tài khoản admin mặc định:
  * Username: admin
  * Password: admin123

### **8.3. Kết nối với pgAdmin**

1️⃣ **Mở pgAdmin**

2️⃣ **Tạo server mới**
* Click chuột phải vào Servers → Register → Server
* Trong tab General:
  * Name: DS Reading Platform (hoặc tên tùy chọn)

* Trong tab Connection:
  * Host name/address: localhost
  * Port: 5433
  * Maintenance database: ds_reading_db
  * Username: postgres
  * Password: wsunicorn

### **8.4. Cấu trúc Docker**

Ứng dụng sử dụng 2 container:
* **Web container**: Chạy Flask application
* **Database container**: Chạy PostgreSQL

Data được lưu trong Docker volumes:
* **postgres_data**: Lưu trữ database
* **uploads_data**: Lưu trữ files upload

### **8.5. Các lệnh Docker hữu ích**

```bash
# Khởi động ứng dụng
docker-compose up

# Chạy ứng dụng ở chế độ nền
docker-compose up -d

# Dừng ứng dụng
docker-compose down

# Xem logs
docker-compose logs

# Xem logs của service cụ thể
docker-compose logs web
docker-compose logs db

# Restart service
docker-compose restart web

# Xóa volumes (cẩn thận, sẽ mất data)
docker-compose down -v
```

### **8.6. Lưu ý quan trọng**

1️⃣ **Bảo mật**
* Thay đổi mật khẩu admin mặc định sau khi cài đặt
* Không chia sẻ file .env
* Đặt mật khẩu mạnh cho database trong môi trường production

2️⃣ **Backup**
* Database được lưu trong Docker volume
* Nên backup định kỳ trong môi trường production
* Có thể export/import data thông qua pgAdmin

3️⃣ **Troubleshooting**
* Nếu gặp lỗi port conflict, kiểm tra và đổi port trong docker-compose.yml
* Nếu không kết nối được database, kiểm tra thông tin trong .env
* Xem logs để debug khi có lỗi xảy ra
