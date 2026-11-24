# AR-IMMS

**AR-Integrated Infrastructure Monitoring and Maintenance System**

Hệ thống giám sát và bảo trì hạ tầng tích hợp thực tế tăng cường,
được phát triển và đánh giá trên Mini Data Center Testbed.

## Người sử dụng

| Vai trò | Trách nhiệm |
| --- | --- |
| System Administrator | Quản trị tài khoản, phân quyền và cấu hình hệ thống |
| System Operator | Quản lý tài sản, giám sát và điều phối bảo trì |
| Technician | Tra cứu thiết bị và thực hiện bảo trì tại hiện trường |

Collector Agent thu thập và gửi telemetry từ môi trường thử nghiệm.

## Cấu trúc repository

```text
CNPM/
├── backend-python/    # Backend Python Flask
├── frontend/          # Web Portal Next.js
├── docs/              # Yêu cầu, thiết kế và báo cáo
├── Checklist.md
├── Skills.md
├── README.md
└── .gitignore
```

## Công nghệ

| Thành phần | Công nghệ |
| --- | --- |
| Backend | Python, Flask |
| Kiến trúc Backend | Clean Architecture |
| ORM | SQLAlchemy |
| Migration | Alembic |
| Database | PostgreSQL |
| Xác thực và phân quyền | JWT, RBAC |
| Web Portal | Next.js, React, TypeScript |
| Tài liệu API | OpenAPI, Swagger UI |
| Kiểm thử Backend | unittest, Flask test client |

Phiên bản thư viện Backend được chốt trong
`backend-python/requirements.txt`.

## Chức năng đã triển khai

- Đăng nhập JWT và xác minh tài khoản hiện tại.
- Phân quyền Administrator, Operator và Technician.
- Danh sách, tạo tài khoản và đổi vai trò.
- CRUD Site, Room, Rack và Server.
- Tra cứu Node cùng Rack, Room, Site và Workload.
- Migration và seed dữ liệu mẫu bằng Python.
- Web Portal có đăng nhập, layout và điều hướng theo vai trò.
- Danh sách, tìm kiếm, lọc và xem chi tiết tài sản trên Web.

## Các phần phát triển tiếp

- Collector Agent và tiếp nhận telemetry.
- Cập nhật dữ liệu và dashboard thời gian thực.
- Cảnh báo, lịch sử telemetry và ticket bảo trì.
- Mobile AR và nhận diện thiết bị.
- Audit, báo cáo và triển khai hệ thống.

## Cài đặt và chạy

1. Cài PostgreSQL và tạo database phát triển trống.
2. Làm theo [README Backend Python](backend-python/README.md)
   để tạo môi trường Python, cấu hình, migration và seed.
3. Khởi động Backend.
4. Làm theo [README Frontend](frontend/README.md) để chạy Web Portal.

Cổng phát triển mặc định:

| Thành phần | Địa chỉ |
| --- | --- |
| Backend Flask | http://localhost:5000 |
| Swagger UI | http://localhost:5000/docs/ |
| OpenAPI JSON | http://localhost:5000/openapi.json |
| Web Portal | http://localhost:3001 |

Frontend cấu hình địa chỉ Backend qua `NEXT_PUBLIC_API_URL`.
Backend cho phép origin Frontend qua `CORS_ORIGINS`.

Không chạy migration khởi tạo Python trên database cũ đã có bảng
được quản lý bằng TypeORM. Xem hướng dẫn Backend để dựng database mới.

## Kết quả kiểm tra

- 13/13 kiểm thử Backend tự động PASS.
- Migration và seed hoạt động trên database trống.
- Chạy lại seed không tạo dữ liệu trùng.
- Bản clone sạch cài đặt và chạy API thành công.
- Frontend đăng nhập và hiển thị chi tiết tài sản qua Flask.

Các kết quả trên được kiểm tra trong môi trường phát triển cục bộ.

## Tài liệu

- [Mục lục tài liệu](docs/README.md)
- [Backend Python](backend-python/README.md)
- [Frontend](frontend/README.md)

Báo cáo sprint trước có thể mô tả giai đoạn triển khai NestJS.
Backend hiện tại sử dụng Python Flask.

## Làm việc nhóm

- Cập nhật mã nguồn trước khi nhận task.
- Tạo nhánh riêng theo công việc.
- Chạy kiểm thử phù hợp và cập nhật tài liệu.
- Gửi Pull Request để review trước khi merge.
- Mỗi thành viên nên có database phát triển riêng.

Không commit `.env`, `.env.migration`, `.venv`, `node_modules`,
cache hoặc thông tin bí mật.

## Giới hạn

Hệ thống được phát triển trên Mini Data Center Testbed.
Kết quả chạy cục bộ chưa chứng minh khả năng vận hành production
hoặc triển khai trong Data Center thực tế.