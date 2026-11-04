# Sprint 1 — Phân tích yêu cầu và thiết kế ban đầu

## 1. Thông tin chung

| Nội dung | Thông tin |
|---|---|
| Dự án | AR-IMMS |
| Phạm vi task | AI-1 đến AI-9 |
| Trọng tâm | Phân tích đề tài, xác định yêu cầu và thiết kế ban đầu |
| Thời gian và phân công | Theo kế hoạch Sprint 1 trên Jira |

Báo cáo tổng hợp tài liệu bàn giao.
Trạng thái hoàn thành từng task được đối chiếu trên Jira.

## 2. Mục tiêu Sprint

Thống nhất vấn đề cần giải quyết, mục tiêu, phạm vi,
người sử dụng và yêu cầu của hệ thống AR-IMMS.

Xây dựng tài liệu làm cơ sở triển khai Backend,
Web Portal, Collector Agent và Mobile AR
trong các sprint tiếp theo.

## 3. Nội dung thực hiện

| Nhóm công việc | Nội dung |
|---|---|
| Phân tích bối cảnh | Xác định môi trường testbed, vấn đề vận hành và nhu cầu bảo trì |
| Xác định mục tiêu | Làm rõ kết quả mong muốn và giới hạn đánh giá của dự án |
| Xác định phạm vi | Phân định chức năng thuộc hệ thống và các tương tác bên ngoài |
| Phân tích tác nhân | Xác định Administrator, Operator, Technician và Collector Agent |
| Yêu cầu chức năng | Xây dựng danh sách FR-01 đến FR-15 |
| Yêu cầu phi chức năng | Xác định các yêu cầu về telemetry, bảo mật, độ tin cậy và giao diện |
| Use Case | Mô tả các luồng sử dụng và liên kết với yêu cầu chức năng |
| Thiết kế ban đầu | Mô tả kiến trúc, cấu trúc tài sản và quan hệ dữ liệu |

Các nhóm nội dung trên không thay thế tiêu đề,
Description và tiêu chí hoàn thành của từng task Jira.

## 4. Nội dung đã thống nhất trong tài liệu

- Hệ thống phục vụ Mini Data Center Testbed.
- Web Portal phục vụ quản trị và vận hành.
- Mobile AR hỗ trợ Technician nhận diện thiết bị và bảo trì.
- Collector Agent thu thập và gửi dữ liệu vận hành.
- Cấu trúc tài sản gồm Site → Room → Rack → Node → Workload.
- Người sử dụng có ba vai trò:
  Administrator, Operator và Technician.
- Backend kiểm tra xác thực và quyền truy cập.
- Cảnh báo và ticket được quản lý theo quy trình riêng.
- Technician cập nhật kết quả; Operator phê duyệt đóng ticket.

## 5. Tài liệu bàn giao

| Nhóm | Đường dẫn |
|---|---|
| Bối cảnh, mục tiêu và phạm vi | [Tổng quan dự án](../00-overview/REAME.md) |
| Tác nhân và phân quyền | [Người sử dụng và RBAC](../01-users-and-rbac/README.md) |
| FR, Use Case và Business Rules | [Yêu cầu chức năng](../02-functional-requirements/README.md) |
| Yêu cầu phi chức năng | [NFR](../03-non-functional-requirements/README.md) |
| Kiến trúc và thiết kế dữ liệu | [Kiến trúc và thiết kế](../04-architecture-and-design/README.md) |

Các liên kết trỏ đến phiên bản tài liệu hiện tại.
Nội dung có thể đã được bổ sung sau Sprint 1.

Khi cần xác định chính xác bản bàn giao cuối Sprint 1,
sử dụng commit hoặc phiên bản tài liệu tương ứng.

## 6. Kiểm tra trước khi nghiệm thu

- Đối chiếu tài liệu với đề tài gốc và task AI-1 đến AI-9.
- Kiểm tra tính thống nhất giữa tác nhân và quyền truy cập.
- Kiểm tra mã FR, NFR và UC không bị trùng hoặc đổi nghĩa.
- Kiểm tra các sơ đồ và liên kết hình ảnh.
- Ghi nhận thông số chưa thống nhất.
- Gắn tài liệu hoặc bằng chứng bàn giao vào task tương ứng.

## 7. Công việc tiếp nối

Sprint 2 sử dụng kết quả phân tích để:

- Khởi tạo Backend NestJS.
- Cấu hình PostgreSQL và migration.
- Xây dựng đăng nhập JWT và RBAC.
- Triển khai API quản lý hạ tầng.
- Kiểm thử và chuẩn bị tích hợp Frontend.

## 8. Giới hạn báo cáo

Việc có tài liệu không tự chứng minh task đã được nghiệm thu.

Ngày hoàn thành, người thực hiện và trạng thái từng task
phải lấy từ Jira hoặc bằng chứng của nhóm.