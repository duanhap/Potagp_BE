1. Mô tả tổng quan Backend

Backend của hệ thống được xây dựng bằng Flask, cung cấp các RESTful API cho ứng dụng mobile và giao diện quản trị.
Hệ thống sử dụng Firebase Authentication để xác thực người dùng. Sau khi người dùng đăng nhập từ ứng dụng, token Firebase sẽ được gửi đến backend để xác thực và lấy thông tin người dùng.

Backend có hai chức năng chính:

1️⃣ API cho ứng dụng mobile

Quản lý dữ liệu người dùng

Quản lý dữ liệu ứng dụng (ví dụ: bài viết, sản phẩm, nội dung, v.v.)

Xử lý nghiệp vụ

2️⃣ Admin dashboard

Quản lý dữ liệu hệ thống

Thêm / sửa / xóa dữ liệu

Quản lý người dùng

2. Cách xác thực (Firebase Auth Flow)

Quy trình xác thực của hệ thống:

1️⃣ Người dùng đăng nhập trên app bằng Firebase Authentication

2️⃣ Firebase trả về ID Token

3️⃣ App gửi request tới backend kèm:

Authorization: Bearer <Firebase ID Token>

4️⃣ Backend dùng Firebase Admin SDK để verify token

5️⃣ Nếu token hợp lệ:

lấy UID

tìm user trong database

xử lý request

3. Kiến trúc Backend

Backend được thiết kế theo MVC kết hợp Repository Pattern, nhằm tách biệt rõ các tầng xử lý.

Các tầng chính
Layer	Chức năng
Controller	nhận request từ client
Service	xử lý business logic
Repository	truy vấn database
Model	định nghĩa cấu trúc dữ liệu

4. CSDL 
-MySQL
-các bảng bao gồm trong file Potago.ddl
-cách kết nối :
SAKURA_DB_USER=avnadmin
SAKURA_DB_PASSWORD=AVNS_6PArOANuuzltVGbJ8L8
SAKURA_DB_HOST=mysql-31a68954-congduan2554-95bb.b.aivencloud.com
SAKURA_DB_PORT=17919
SAKURA_DB_NAME=potago

5. Admin Dashboard

Backend cũng cung cấp giao diện admin để quản lý hệ thống.

-Admin có thể:

xem danh sách user
xem thống kê

-Giao diện admin xây bằng:

HTML + Flask template

