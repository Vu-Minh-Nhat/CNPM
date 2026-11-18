# Task 49 — Alert & Ticket: Business Rules and Lifecycle

## 1. Mục tiêu

Thống nhất dữ liệu, quyền thao tác và luồng xử lý trước khi Backend và Frontend triển khai song song.

## 2. Phạm vi

Task này thống nhất:

- Cấu hình và xử lý cảnh báo CPU, RAM, Disk.
- Quy tắc dữ liệu thiếu, dữ liệu cũ, bản tin đến muộn và bản tin gửi lại.
- Vòng đời cảnh báo.
- Vòng đời ticket.
- Ma trận quyền Administrator, Operator và Technician.
- Lịch sử nghiệp vụ và audit.
- Các điểm cần chốt trước khi Backend và Frontend implementation.

## 3. Nguồn tham chiếu

Task 49 được đối chiếu với:

- FR-09 — Alert monitoring.
- FR-10 — Ticket creation and assignment.
- FR-11 — Ticket processing and approval.
- FR-13 — Monitoring configuration.
- FR-14 — Audit.
- Business Rules hiện có.
- Role/Permission hiện có.
- Non-functional requirements hiện có.
- Telemetry storage contract hiện có.

## 4. Quy tắc dữ liệu telemetry

### 4.1 CPU, RAM và Disk

Các metric được sử dụng:

- CPU: `cpu_percent`
- RAM: `memory_percent`
- Disk: `disk_percent`

Đơn vị:

- `%`
- Giá trị hợp lệ: `0..100`

### 4.2 Timestamp

Telemetry phải có timestamp.

Timestamp được chuẩn hóa về UTC.

Dữ liệu đến muộn không được mặc định xem là dữ liệu hiện tại.

### 4.3 Bản tin gửi lại

Khi Agent gửi lại cùng một telemetry message:

- `message_id` phải được giữ nguyên.
- Backend phải nhận diện duplicate message.
- Duplicate telemetry được xử lý theo chính sách telemetry duplicate.
- Duplicate telemetry không được tạo ra duplicate alert.

### 4.4 Dữ liệu thiếu và dữ liệu cũ

Dữ liệu thiếu không được hiểu là giá trị `0`.

Dữ liệu cũ phải được phân biệt với dữ liệu hiện tại.

UI phải có khả năng thể hiện thời điểm cập nhật gần nhất và trạng thái dữ liệu.

## 5. Freshness và mất kết nối

Theo phạm vi Task 49:

- Dữ liệu được xem là cũ khi quá `30 giây`.
- Node được xem là mất kết nối khi quá `90 giây` kể từ lần tiếp nhận hợp lệ gần nhất.

Quy tắc này phải được Backend và Frontend sử dụng thống nhất.

> Lưu ý: tài liệu NFR hiện có đã chốt mốc mất kết nối `>90 giây`, nhưng stale threshold `30 giây` cần được ghi nhận là quyết định của Task 49 để tránh hiểu khác nhau giữa Backend và Frontend.

## 6. Cấu hình cảnh báo

Alert condition cần thống nhất các thành phần:

- Metric.
- Operator.
- Threshold.
- Severity.
- Recovery condition.

Các metric chính:

- CPU.
- RAM.
- Disk.

Ví dụ cấu trúc điều kiện:

```text
metric + operator + threshold → severity