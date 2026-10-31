# Kiểm thử bổ sung Backend — Sprint 2
Ngày kiểm tra: 31/10/2026
Branch: codex/fix-sprint-2

## Phạm vi sửa

- Bổ sung phân quyền cho API Site, Room, Rack và Server.
- Chặn endpoint chưa khai báo quyền.
- Sửa DTO tạo Site khớp schema PostgreSQL và sinh UUID.
- Sửa cập nhật khóa ngoại Room, Rack và Server.
- Chuyển lỗi dữ liệu thành phản hồi HTTP phù hợp.
- Kết nối JwtAuthGuard với Passport JwtStrategy.
- Thống nhất khóa ký và kiểm tra JWT.
- Bổ sung Bearer authentication trong Swagger.
- Sửa cấu hình và dependency giả lập của unit test.
- Giới hạn Vitest chạy test trong Backend chính.

## Môi trường

- Backend NestJS.
- PostgreSQL trên máy phát triển.
- Tài khoản và dữ liệu mẫu từ migration/seed.
- Kiểm tra API bằng PowerShell và Swagger UI.

## Kết quả tự động

| Kiểm tra | Kết quả |
|---|---|
| Build | Thành công |
| Unit test | 9 file, 20 test đạt |
| E2E test | 3 file, 17 test đạt |

## Kết quả kiểm tra API thủ công

| Trường hợp | Kết quả |
|---|---|
| Technician xem Site/Room/Rack/Server | 200 |
| Technician tạo tài sản | 403 |
| Operator xóa tài sản | 403 |
| Operator tạo, cập nhật và đọc lại cây tài sản thử nghiệm | Thành công |
| Tạo Site trùng mã | 409 |
| Tạo Site thiếu mã | 400 |
| Cập nhật Server trùng mã | 409 |
| Chuyển Server sang Rack không tồn tại | 400 |
| Chuyển Room sang Site không tồn tại | 400 |
| Chuyển Rack sang Room không tồn tại | 400 |
| Quan hệ gốc sau cập nhật thất bại | Giữ nguyên |
| Administrator xóa Site/Room/Rack còn dữ liệu con | 409 |
| Đăng nhập đúng trên Swagger | 200 |
| Truy cập API với token hợp lệ | 200 |
| GET /auth/me không có token | 401 |
| Xóa cây tài sản thử nghiệm từ con đến cha | Thành công |
| Đọc lại bốn bản ghi đã xóa | 404 |

Tên tiếng Việt được kiểm tra bằng request JSON UTF-8.

## Dữ liệu thử nghiệm

Tạo riêng một cây Site → Room → Rack → Server.
Sau kiểm tra, đã xóa toàn bộ cây thử nghiệm và xác nhận 404.
Không sử dụng tài sản thật để kiểm tra xóa.

## Giới hạn

- Các endpoint ghi `/assets` tổng quát vẫn chưa triển khai.
- CRUD hạ tầng được thực hiện qua `/sites`, `/rooms`,
  `/racks` và `/servers`.
- Chưa đánh giá Frontend trong lần kiểm tra này.
- Báo cáo này ghi nhận các kiểm tra đã thực hiện,
  không thay thế việc đối chiếu toàn bộ task trên Jira.
  ## AI-33 — Kiểm tra dựng lại môi trường

### Cách thực hiện

- Clone mới branch `codex/fix-sprint-2` từ GitHub.
- Commit được kiểm tra: `f6b548e`.
- Sử dụng thư mục kiểm thử riêng.
- Tạo database trống `arimms_sprint2_check`.
- Tạo `.env` từ `.env.example` và cấu hình riêng.
- Chạy Backend ở cổng 3002.

### Kết quả

| Kiểm tra | Kết quả |
|---|---|
| npm ci | Thành công |
| Kết nối database | Thành công |
| Build | Thành công |
| Migration trên database mới | Thành công |
| Seed dữ liệu mẫu | Thành công |
| Unit test | 20 test đạt |
| E2E test | 17 test đạt |
| GET /health | Trả status ok |
| Swagger /api | Truy cập được |
| Đăng nhập tài khoản mẫu | Thành công |
| GET /users có token | 200, có dữ liệu mẫu |
| GET /assets có token | 200, có dữ liệu mẫu |

### Phạm vi xác nhận

Đã kiểm tra bản clone sạch với database mới trên cùng máy.
Chưa trực tiếp kiểm tra trên máy thành viên khác.

### Vấn đề được ghi nhận

npm ci báo 11 lỗ hổng dependency:
2 low, 4 moderate và 5 high.
Các cảnh báo này chưa được phân tích hoặc khắc phục
trong lần kiểm tra dựng môi trường.