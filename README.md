# **Data Sience Reading Sharing Platform**

**Xây dựng nền tảng chia sẻ nội dung thông minh hỗ trợ người dùng trao đổi và lan tỏa tri thức (DS Reading Sharing Platform)

---

## **1. THÔNG TIN NHÓM**

* Nguyễn Ngọc Lân – nguyenngoclan120904@gmail.com
* Ngô Trường Định -
* Nguyễn Tấn Minh
* Phan Thành Đạt

---

## **2. MÔ TẢ ĐỀ TÀI**

### **2.1. Mô tả tổng quan**

Trong thời đại bùng nổ thông tin, việc chia sẻ những bài viết hay, nguồn học liệu chất lượng là điều cần thiết. Tuy nhiên, các nền tảng hiện tại thường thiếu công cụ hỗ trợ cá nhân hóa nội dung hoặc hỗ trợ người dùng tóm tắt bài viết nhanh chóng.

Đề tài của chúng tôi là một nền tảng web mang tên **DS Reading Sharing Platform** – nơi người dùng có thể chia sẻ link bài viết, nhận tóm tắt nội dung và tương tác với chatbot hỗ trợ viết content. Web app này ứng dụng trí tuệ nhân tạo thông qua API của **Gemini** để hỗ trợ người dùng:

* Soạn nội dung dễ dàng.
* Tóm tắt các bài viết dài.
* Tự động đăng bài viết đã xử lý.
* Tương tác cơ bản như like, comment, lưu bài viết hay về kho lưu trữ,... cũng được thực hiện trên web app của chúng tôi.

Trang web còn hỗ trợ lưu trữ dữ liệu với PostgreSQL và Firebase, tích hợp Docker để đảm bảo khả năng triển khai dễ dàng trên **Google Cloud Platform** thông qua Cloud Run, Cloud SQL và hỗ trợ realtime nhờ Flask-SocketIO.

### **2.2. Mục tiêu**

* Xây dựng một nền tảng chia sẻ tri thức thân thiện, dễ sử dụng.
* Tích hợp AI hỗ trợ người dùng đọc nhanh, viết nhanh, chia sẻ nhanh.
* Ứng dụng công nghệ hiện đại như Docker, Cloud, Realtime, AI vào một sản phẩm hoàn chỉnh.

---

## **3. PHÂN TÍCH THIẾT KẾ**

### **3.1. Phân tích yêu cầu**

* **Chức năng**:

  * Người dùng có thể chia sẻ đường link bài viết.
  * Hệ thống tự động gọi API để tóm tắt nội dung bài viết.
  * Tích hợp chatbot (Gemini API) hỗ trợ soạn nội dung hoặc trả lời câu hỏi.
  * Người dùng có thể tương tác realtime.
  * Tạo tài khoản, đăng nhập và lưu trữ dữ liệu bài viết đã chia sẻ.
* **Phi chức năng**:

  * Hệ thống phải xử lý nhanh, tối ưu trải nghiệm người dùng.
  * Giao diện responsive, dễ dùng trên mọi thiết bị.
  * Khả năng mở rộng tốt (scalable) thông qua container hóa và Cloud Run.

### **3.2. Đặc tả yêu cầu**

* **Chức năng 1: Gửi link bài viết**

  * Giao diện có input để người dùng dán link.
  * Backend gọi Gemini API để tóm tắt nội dung.
  * Nội dung được hiển thị trong giao diện và có thể chia sẻ công khai.
* **Chức năng 2: Tương tác với chatbot**

  * Có khung chat hỗ trợ Gemini API.
  * Người dùng có thể yêu cầu viết content, tóm tắt, trả lời câu hỏi,…
* **Chức năng 3: Đăng nhập và quản lý bài viết**

  * Firebase Authentication.
  * Người dùng có thể xem lại lịch sử bài đã chia sẻ.

### **3.3. Thiết kế hệ thống**

* **Use case diagram**:
  (Vẽ sơ đồ mô tả người dùng tương tác với chatbot, chia sẻ bài, xem bài tóm tắt, v.v.)
* **Thiết kế CSDL**:

  * PostgreSQL: lưu metadata các bài viết, nội dung tóm tắt, nội dung do chatbot tạo.
  * Firebase: xác thực người dùng và lưu realtime tương tác.
* **Thiết kế giao diện**:

  * Trang chủ: ô nhập link + kết quả tóm tắt.
  * Trang chat: tích hợp chatbot.
  * Trang đăng ký/đăng nhập.
  * Lịch sử các bài viết đã chia sẻ.

---

## **4. CÔNG CỤ VÀ CÔNG NGHỆ SỬ DỤNG**

* **Ngôn ngữ lập trình**: Python, JavaScript
* **Backend**: Flask + Flask-SocketIO
* **Frontend**: HTML, TailwindCSS, JavaScript
* **AI API**: Gemini API (Google)
* **Cơ sở dữ liệu**: PostgreSQL + Firebase Realtime
* **IDE**: Visual Studio Code
* **Triển khai**: Docker, Google Cloud Platform (Cloud Run, Cloud SQL)

---

## **5. TRIỂN KHAI**

### **5.1. Quy trình xây dựng hệ thống**

1. Thiết kế frontend bằng HTML + Tailwind.
2. Xây dựng backend Flask: routing, gọi API, xử lý dữ liệu.
3. Tích hợp SocketIO để hỗ trợ tương tác realtime.
4. Dùng Docker để tạo image.
5. Deploy trên Google Cloud Platform:

   * Cloud Run (chạy container).
   * Cloud SQL (PostgreSQL).
   * Firebase (Auth + Realtime).
### **5.2. Hướng dẫn cài đặt và chạy web app**
#### **5.2.1. Yêu cầu hệ thống**
* Docker Desktop
* Git
* pgAdmin (tùy chọn - để quản lý database)

#### **5.2.2. Các bước cài đặt**

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
  * Email: admin@admin.com
  * Password: admin123

### **5.2.3. Kết nối với pgAdmin**

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

### **5.2.4. Cấu trúc Docker**

Ứng dụng sử dụng 2 container:
* **Web container**: Chạy Flask application
* **Database container**: Chạy PostgreSQL

Data được lưu trong Docker volumes:
* **postgres_data**: Lưu trữ database
* **uploads_data**: Lưu trữ files upload

### **5.2.5. Các lệnh Docker hữu ích**

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

### **5.2.6. Lưu ý quan trọng**

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
---

## **6. KIỂM THỬ**

* **Functional Testing**:

  * Kiểm tra từng chức năng: chia sẻ link, hiển thị tóm tắt, trò chuyện với chatbot,...
* **Performance Testing**:

  * Đo thời gian phản hồi khi gửi link.
  * Kiểm thử đồng thời nhiều người dùng tương tác với chatbot.

---

## **7. KẾT QUẢ**

### **7.1. Kết quả đạt được**

* Nền tảng chia sẻ nội dung hoạt động ổn định.
* Tích hợp thành công Gemini API cho các tác vụ viết và tóm tắt.
* Realtime tương tác chatbot bằng SocketIO hoạt động mượt.
* Hệ thống đã được container hóa và sẵn sàng cho triển khai trên Cloud.

### **7.2. Kết quả chưa đạt được**

* Chưa có hệ thống gợi ý nội dung theo sở thích người dùng.
* Tốc độ tóm tắt chưa tối ưu với bài viết rất dài.

### **7.3. Hướng phát triển**

* Bổ sung hệ thống gợi ý nội dung theo profile người dùng (machine learning).
* Thêm tính năng like, comment, share nội dung.
* Tối ưu chatbot để hiểu ngữ cảnh sâu hơn.
* Tạo mobile app (sử dụng Flutter hoặc React Native).

---

## **8. TÀI LIỆU THAM KHẢO**

* \[[https://flutter.dev](https://flutter.dev)]
* \[[https://dart.dev](https://dart.dev)]
* \[[https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)]
* \[[https://cloud.google.com/run](https://cloud.google.com/run)]
* \[[https://cloud.google.com/sql](https://cloud.google.com/sql)]
* \[[https://firebase.google.com](https://firebase.google.com)]
* \[[https://ai.google.dev/gemini-api/docs](https://ai.google.dev/gemini-api/docs)]
* [TailwindCSS Documentation](https://tailwindcss.com/docs)

---

Nếu bạn cần mình vẽ sơ đồ **Use case diagram** hoặc hỗ trợ thiết kế database / frontend wireframe, chỉ cần hú là mình làm ngay!
