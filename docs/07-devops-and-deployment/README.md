# Cài đặt, cấu hình và vận hành

## 1. Mục đích

Hướng dẫn thành viên tìm đúng tài liệu để cài đặt,
cấu hình và chạy AR-IMMS.

Tài liệu phục vụ yêu cầu bàn giao môi trường của AI-33
và việc tích hợp các thành phần trong những sprint tiếp theo.

## 2. Hướng dẫn cài đặt

| Thành phần | Tài liệu |
|---|---|
| Tổng quan repository | [README dự án](../../README.md) |
| Backend, database, migration và seed | [Backend README](../../backend/README.md) |
| Frontend, cấu hình API và chạy Web Portal | [Frontend README](../../frontend/README.md) |

Các lệnh cài đặt và chạy được duy trì trong README
của từng thành phần.

## 3. Cấu hình môi trường phát triển

| Thành phần | Cấu hình mặc định |
|---|---|
| Backend | http://localhost:3000 |
| Frontend | http://localhost:3001 |
| PostgreSQL | localhost:5432 hoặc cổng đã cấu hình |

Địa chỉ và cổng thực tế phụ thuộc môi trường của từng thành viên.

localhost luôn chỉ máy đang chạy thành phần đó,
không phải địa chỉ dùng chung giữa các máy.

## 4. Biến môi trường

| Thành phần | File mẫu | File cấu hình trên máy | Biến chính |
|---|---|---|---|
| Backend | backend/.env.example | backend/.env | DATABASE_URL, JWT_SECRET, PORT, CORS_ORIGINS |
| Frontend | frontend/.env.example | frontend/.env.local | NEXT_PUBLIC_API_URL |

### Nguyên tắc

- Sao chép file mẫu và điền giá trị phù hợp với máy.
- Không commit file cấu hình có mật khẩu hoặc thông tin bí mật.
- Không đặt JWT_SECRET hoặc mật khẩu database vào Frontend.
- Biến NEXT_PUBLIC_* có thể được đưa vào mã chạy trên trình duyệt.
- Khởi động lại ứng dụng sau khi thay đổi cấu hình.
- Khi build Frontend cho môi trường khác,
  phải sử dụng địa chỉ API phù hợp tại thời điểm build.

## 5. Database và migration

### Database phát triển riêng

Mỗi thành viên có thể sử dụng database riêng
và chạy cùng bộ migration từ repository.

Cách này giúp thử nghiệm mà không thay đổi dữ liệu
của các thành viên khác.

### Database dùng chung

Nếu nhóm sử dụng database chung:

- Chỉ định người phụ trách migration.
- Không chạy migration đồng thời từ nhiều máy.
- Không chạy seed, reset hoặc xóa dữ liệu tùy ý.
- Phân biệt dữ liệu kiểm thử và dữ liệu cần giữ.
- Sao lưu trước thay đổi có khả năng mất dữ liệu.

Database không được tự đồng bộ dữ liệu qua Git.
Git quản lý mã nguồn, migration và tài liệu.

## 6. Tích hợp Frontend và Backend

1. Khởi động PostgreSQL.
2. Kiểm tra kết nối database của Backend.
3. Áp dụng migration theo hướng dẫn và trạng thái database.
4. Khởi động Backend.
5. Cấu hình NEXT_PUBLIC_API_URL của Frontend.
6. Cho phép địa chỉ Frontend trong cấu hình CORS của Backend.
7. Khởi động Frontend.
8. Kiểm tra /health và đăng nhập qua trình duyệt.

Không chạy lại seed nếu chưa xác định mục đích
và ảnh hưởng đến database đang sử dụng.

## 7. Kiểm tra sau khi cập nhật mã nguồn

- Đọc thay đổi cấu hình và hướng dẫn liên quan.
- Chạy npm ci trong thành phần tương ứng
  khi cần đồng bộ dependency theo package-lock.json.
- Kiểm tra trạng thái migration nếu có thay đổi database.
- Chạy lint, build và các kiểm thử liên quan đến thay đổi.
- Kiểm tra lại luồng tích hợp bị ảnh hưởng.

Không đưa node_modules, .next, dist hoặc file .env thật
vào commit.

## 8. Phạm vi vận hành hiện tại

Hướng dẫn hiện tại tập trung vào môi trường phát triển
và kiểm thử Mini Data Center Testbed.

Không suy ra hệ thống đã triển khai production
chỉ từ việc chạy thành công trên localhost.

Thông tin hosting, tên miền, HTTPS, sao lưu định kỳ
và quy trình triển khai được bổ sung khi nhóm thực hiện
task triển khai tương ứng.

## 9. Bằng chứng kiểm tra môi trường

Xem [Báo cáo kiểm thử Backend Sprint 2](../06-testing-and-qa/sprint-2-backend.md).

Báo cáo ghi nhận việc dựng lại môi trường bằng bản clone sạch
và database mới trên cùng máy phát triển.

Kiểm chứng trên máy thành viên khác phải có kết quả riêng.
