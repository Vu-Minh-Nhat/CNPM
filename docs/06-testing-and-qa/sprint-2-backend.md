# Báo cáo kiểm thử Backend — Sprint 2

## 1. Thông tin kiểm thử

| Nội dung | Thông tin |
|---|---|
| Dự án | AR-IMMS |
| Task liên quan | AI-27, AI-29, AI-30, AI-31, AI-32, AI-33 |
| Ngày thực hiện | 31/10/2026 |
| Nhánh kiểm thử | codex/fix-sprint-2 |
| Công cụ | Vitest, PowerShell, Swagger UI, PostgreSQL |

Báo cáo ghi nhận kết quả tại thời điểm kiểm thử.
Các thay đổi mã nguồn sau đó cần được kiểm tra lại khi có ảnh hưởng.

## 2. Mục tiêu

- Kiểm tra Backend khởi động và kết nối database.
- Kiểm tra migration và dữ liệu mẫu.
- Kiểm thử đăng nhập, JWT và RBAC.
- Kiểm thử API Site, Room, Rack và Server.
- Kiểm tra khả năng dựng lại môi trường theo hướng dẫn.

## 3. Môi trường

- Backend NestJS.
- PostgreSQL trên máy phát triển.
- Database được khởi tạo bằng migration.
- Tài khoản mẫu gồm Administrator, Operator và Technician.
- Dữ liệu kiểm thử được tạo riêng.

Không đưa mật khẩu, JWT hoặc DATABASE_URL thật vào báo cáo.

## 4. Kết quả kiểm thử tự động

| Hạng mục | Kết quả |
|---|---|
| Backend build | Thành công |
| Unit test | 9 file, 20 test đạt |
| E2E test | 3 file, 17 test đạt |

Kết quả tự động được bổ sung bằng kiểm tra API thủ công.
Không mặc định mọi trường hợp thủ công đã có test tự động tương ứng.

## 5. Kết quả kiểm thử API

| Mã | Trường hợp | Kết quả mong đợi | Kết quả thực tế |
|---|---|---|---|
| BE-01 | Đăng nhập bằng tài khoản hợp lệ | 200 và có access token | Đạt |
| BE-02 | GET /auth/me không có token | 401 | Đạt |
| BE-03 | Truy cập API được phép với token hợp lệ | 200 | Đạt |
| BE-04 | Technician xem Site, Room, Rack và Server | 200 | Đạt |
| BE-05 | Technician tạo tài sản hạ tầng | 403 | Đạt |
| BE-06 | Operator xóa tài sản hạ tầng | 403 | Đạt |
| BE-07 | Operator tạo, cập nhật và đọc lại cây tài sản | Dữ liệu được lưu và truy vấn đúng | Đạt |
| BE-08 | Tạo Site trùng mã | 409 | Đạt |
| BE-09 | Tạo Site thiếu mã | 400 | Đạt |
| BE-10 | Cập nhật Server thành mã đã tồn tại | 409 | Đạt |
| BE-11 | Chuyển Server sang Rack không tồn tại | 400 | Đạt |
| BE-12 | Chuyển Room sang Site không tồn tại | 400 | Đạt |
| BE-13 | Chuyển Rack sang Room không tồn tại | 400 | Đạt |
| BE-14 | Đọc lại quan hệ sau cập nhật thất bại | Giữ nguyên quan hệ cũ | Đạt |
| BE-15 | Administrator xóa Site, Room hoặc Rack còn dữ liệu con | 409 | Đạt |
| BE-16 | Xóa cây tài sản thử nghiệm từ con đến cha | Xóa thành công | Đạt |
| BE-17 | Đọc lại các bản ghi đã xóa | 404 | Đạt |
| BE-18 | Tạo hoặc cập nhật tên tiếng Việt bằng JSON UTF-8 | Lưu và đọc lại đúng nội dung | Đạt |

## 6. Dữ liệu thử nghiệm

Tạo riêng cây dữ liệu:

Site → Room → Rack → Server

Sau khi kiểm tra:

- Xóa Server trước, sau đó Rack, Room và Site.
- Xác nhận truy vấn lại bốn bản ghi trả về 404.
- Không sử dụng tài sản thật để kiểm thử thao tác xóa.

## 7. Kiểm tra dựng lại môi trường

### Cách thực hiện

- Clone mới nhánh codex/fix-sprint-2.
- Commit được kiểm tra: f6b548e.
- Sử dụng thư mục kiểm thử riêng.
- Tạo database trống arimms_sprint2_check.
- Cấu hình .env từ .env.example.
- Chạy Backend ở cổng 3002.

### Kết quả

| Hạng mục | Kết quả |
|---|---|
| npm ci | Thành công |
| Kết nối database | Thành công |
| Build | Thành công |
| Chạy migration trên database mới | Thành công |
| Seed dữ liệu mẫu | Thành công |
| Unit test | 20 test đạt |
| E2E test | 17 test đạt |
| GET /health | Trả status ok |
| Swagger UI | Truy cập được |
| Đăng nhập tài khoản mẫu | Thành công |
| GET /users với token Administrator | 200 và có dữ liệu mẫu |
| GET /assets với token hợp lệ | 200 và có dữ liệu mẫu |

Đây là kiểm tra trên bản clone sạch và database mới
trên cùng máy phát triển.

Chưa dùng kết quả này để khẳng định đã kiểm chứng
trên máy thành viên khác.

## 8. Vấn đề dependency tại thời điểm kiểm thử

Trong lần dựng môi trường, npm ci báo:

- 2 mức low.
- 4 mức moderate.
- 5 mức high.

Đây là số liệu tại thời điểm kiểm thử,
không phải kết quả audit hiện tại.

Việc khắc phục và xác nhận lại dependency
được theo dõi riêng, kèm kết quả npm audit mới.

## 9. Giới hạn

- Các thao tác ghi tại /assets tổng quát chưa được triển khai.
- CRUD hạ tầng sử dụng /sites, /rooms, /racks và /servers.
- Báo cáo này không đánh giá Frontend.
- Chưa đánh giá tải lớn, kiểm thử xâm nhập
  hoặc toàn bộ yêu cầu phi chức năng.
- Kết quả đạt trong báo cáo không tự xác nhận
  tất cả task Jira của dự án đã hoàn thành.

## 10. Kết luận

Backend đạt các trường hợp kiểm thử được liệt kê
trong môi trường phát triển tại thời điểm kiểm tra.

Việc nghiệm thu AI-33 còn cần đối chiếu hướng dẫn cấu hình,
tài liệu API, kết quả bàn giao và tiêu chí trên Jira.

## 11. Tài liệu liên quan

- [Hướng dẫn Backend](../../backend/README.md)
- [Quy tắc nghiệp vụ](../02-functional-requirements/business-rules.md)
- [Yêu cầu phi chức năng](../03-non-functional-requirements/non-functional-requirements.md)