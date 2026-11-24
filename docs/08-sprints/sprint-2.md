# Sprint 2 — Backend lõi

## 1. Thông tin chung

| Nội dung | Thông tin |
|---|---|
| Dự án | AR-IMMS |
| Thời gian kế hoạch | 15/10/2026 – 31/10/2026 |
| Trọng tâm | Backend, database, xác thực, phân quyền và API hạ tầng |
| Phạm vi | AI-27, AI-29, AI-30, AI-31, AI-32, AI-33 |

Trạng thái công việc chính thức được theo dõi trên Jira.
Báo cáo này tổng hợp kết quả và bằng chứng bàn giao.

## 2. Mục tiêu Sprint

Xây dựng Backend lõi bằng NestJS, TypeScript và PostgreSQL,
bao gồm:

- Cấu hình dự án và môi trường phát triển.
- Kết nối database, migration và dữ liệu mẫu.
- Đăng nhập và xác thực JWT.
- Phân quyền Administrator, Operator và Technician.
- API quản lý Site, Room, Rack và Server.
- Kiểm thử và hướng dẫn chạy để chuẩn bị tích hợp Frontend.

## 3. Danh sách công việc

| Task | Nội dung | Kết quả bàn giao |
|---|---|---|
| AI-27 | Khởi tạo NestJS Backend API | Cấu trúc Backend, cấu hình chung và hướng dẫn chạy |
| AI-29 | Thiết kế và khởi tạo database | Kết nối PostgreSQL, migration, ràng buộc và dữ liệu mẫu |
| AI-30 | Xây dựng API đăng nhập và xác thực JWT | POST /auth/login, xác minh JWT và thông tin tài khoản |
| AI-31 | Xây dựng phân quyền RBAC | Kiểm tra quyền tại Backend theo ba vai trò |
| AI-32 | API quản lý Site, Room, Rack và Server | Các endpoint CRUD, kiểm tra dữ liệu và quan hệ tài sản |
| AI-33 | Kiểm thử API và bảo mật | Kết quả kiểm thử, tài liệu API và hướng dẫn cấu hình môi trường |

## 4. Kết quả triển khai

### 4.1. Backend và database

- Backend được tổ chức theo module.
- Kết nối PostgreSQL qua biến môi trường.
- Cấu trúc database được khởi tạo bằng migration.
- Có dữ liệu mẫu phục vụ phát triển và kiểm thử.
- Backend có thể truy vấn tài khoản và tài sản từ database.

### 4.2. Xác thực và phân quyền

- Đăng nhập trả JWT khi tài khoản hợp lệ.
- API được bảo vệ kiểm tra JWT.
- Backend kiểm tra tài khoản và vai trò.
- Phân biệt lỗi chưa xác thực và không đủ quyền.
- Swagger hỗ trợ nhập Bearer token để kiểm thử.

### 4.3. Quản lý hạ tầng

- Có API Site, Room, Rack và Server.
- Cả ba vai trò được xem dữ liệu theo quyền đã thiết lập.
- Administrator và Operator được tạo, cập nhật.
- Chỉ Administrator được xóa.
- Kiểm tra mã trùng và tham chiếu tài sản cha.
- Ngăn xóa tài sản còn dữ liệu phụ thuộc.
- Giữ nguyên quan hệ khi cập nhật không hợp lệ.

## 5. Kết quả kiểm thử

Kết quả được ghi nhận ngày 31/10/2026:

| Hạng mục | Kết quả |
|---|---|
| Backend build | Thành công |
| Unit test | 20 test đạt |
| E2E test | 17 test đạt |
| CRUD cây tài sản thử nghiệm | Đạt các trường hợp đã ghi nhận |
| JWT và RBAC | Đạt các trường hợp đã ghi nhận |
| Ràng buộc dữ liệu | Đạt các trường hợp đã ghi nhận |
| Dựng lại từ bản clone sạch và database mới | Thành công trên cùng máy phát triển |

Chi tiết:
[Báo cáo kiểm thử Backend](../06-testing-and-qa/sprint-2-backend.md).

Kết quả trên không thay thế kiểm thử lại
khi các thay đổi mới ảnh hưởng đến chức năng liên quan.

## 6. Vấn đề đã xử lý

| Vấn đề | Hướng xử lý |
|---|---|
| DTO tạo Site chưa khớp dữ liệu lưu trữ | Điều chỉnh dữ liệu đầu vào và tạo UUID |
| Cập nhật quan hệ Room, Rack, Server chưa đúng | Điều chỉnh cập nhật khóa ngoại và kiểm tra lại dữ liệu |
| Lỗi database trả về phản hồi chưa phù hợp | Ánh xạ các lỗi đã xử lý sang HTTP 400 hoặc 409 |
| Luồng JWT chưa thống nhất | Kết nối Guard với Strategy và thống nhất cấu hình JWT |
| Unit test thiếu dependency giả lập | Cập nhật cấu hình và mock phù hợp |
| Phạm vi chạy test có thể chứa bản clone lồng | Giới hạn đường dẫn kiểm thử của Backend chính |

## 7. Giới hạn và công việc tiếp nối

- Các thao tác ghi tại /assets tổng quát chưa được triển khai;
  sử dụng API hạ tầng tương ứng cho CRUD.
- Chưa xác nhận chạy trên máy thành viên khác
  chỉ từ kết quả clone sạch trên cùng máy.
- Cảnh báo dependency được ghi nhận và theo dõi riêng.
- Telemetry, Agent, cảnh báo, ticket và Mobile AR
  được thực hiện theo các task tiếp theo.
- Frontend được phát triển và kiểm thử trong sprint tương ứng.

## 8. Tài liệu bàn giao

- [Hướng dẫn Backend](../../backend/README.md)
- [Kiến trúc hệ thống](../04-architecture-and-design/system-architecture.md)
- [Thiết kế ERD](../04-architecture-and-design/erd.md)
- [Kiểm thử Backend](../06-testing-and-qa/sprint-2-backend.md)
- [Cấu hình và vận hành](../07-devops-and-deployment/README.md)

## 9. Liên kết Jira

- [AI-27](https://phamvanut12121958.atlassian.net/browse/AI-27)
- [AI-29](https://phamvanut12121958.atlassian.net/browse/AI-29)
- [AI-30](https://phamvanut12121958.atlassian.net/browse/AI-30)
- [AI-31](https://phamvanut12121958.atlassian.net/browse/AI-31)
- [AI-32](https://phamvanut12121958.atlassian.net/browse/AI-32)
- [AI-33](https://phamvanut12121958.atlassian.net/browse/AI-33)

Mỗi task cần gắn PR, mã nguồn hoặc bằng chứng tương ứng.
Việc chuyển Done và đóng sprint thực hiện theo quy trình nhóm.