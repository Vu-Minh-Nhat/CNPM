# Các tác nhân của hệ thống AR-IMMS

## 1. Mục đích

Xác định các tác nhân tương tác với AR-IMMS và trách nhiệm
của từng tác nhân trong quá trình quản trị, vận hành và bảo trì.

Hệ thống có ba vai trò người sử dụng:
Administrator, Operator và Technician.

Collector Agent là tác nhân phần mềm thu thập dữ liệu.

## 2. System Administrator

### Trách nhiệm

Quản trị tài khoản, quyền truy cập và cấu hình hệ thống.

### Nhu cầu sử dụng

- Đăng nhập và đăng xuất.
- Quản lý tài khoản và gán vai trò.
- Kích hoạt hoặc vô hiệu hóa tài khoản.
- Quản lý cấu hình thuộc phạm vi quản trị.
- Theo dõi sức khỏe hệ thống.
- Tra cứu audit log.
- Quản lý tài sản theo quyền được cấp.

### Giao diện

Web Management Portal.

### Giá trị vai trò trong Backend

`Administrator`

## 3. System Operator

### Trách nhiệm

Giám sát hạ tầng và điều phối công việc xử lý sự cố, bảo trì.

### Nhu cầu sử dụng

- Đăng nhập và đăng xuất.
- Tra cứu, tạo và cập nhật tài sản theo quyền được cấp.
- Theo dõi telemetry và trạng thái kết nối.
- Cấu hình điều kiện cảnh báo theo phạm vi được cấp.
- Theo dõi và xử lý cảnh báo.
- Tạo, phân công và theo dõi ticket.
- Kiểm tra kết quả xử lý và phê duyệt đóng ticket.
- Tra cứu lịch sử vận hành và báo cáo.

### Giao diện

Web Management Portal.

### Giá trị vai trò trong Backend

`Operator`

## 4. Technician

### Trách nhiệm

Thực hiện các công việc kiểm tra, xử lý sự cố và bảo trì được giao.

### Nhu cầu sử dụng

- Đăng nhập và đăng xuất.
- Xem ticket được giao.
- Tra cứu tài sản theo quyền được cấp.
- Quét marker để xác định thiết bị.
- Xem thông tin thiết bị và telemetry phục vụ kiểm tra.
- Cập nhật tiến độ, kết quả và bằng chứng bảo trì.
- Gửi kết quả để Operator kiểm tra và phê duyệt đóng ticket.

### Giao diện

Ứng dụng Mobile AR trên Android.

Web Portal cung cấp các trang tra cứu được cấp quyền
theo phạm vi thiết kế.

### Giá trị vai trò trong Backend

`Technician`

## 5. Collector Agent

### Trách nhiệm

Thu thập dữ liệu vận hành của Node và Workload,
sau đó gửi về Backend.

### Tương tác

- Gửi telemetry cùng thời điểm ghi nhận.
- Gửi thông tin phục vụ xác định trạng thái kết nối.
- Nhận cấu hình thu thập theo cơ chế được thống nhất.
- Thực hiện retry và phục hồi kết nối theo chính sách hệ thống.

Chu kỳ thu thập, gửi dữ liệu và heartbeat được quy định
trong tài liệu yêu cầu phi chức năng và thiết kế Agent.

### Cơ chế xác thực

Collector Agent sử dụng thông tin xác thực riêng theo thiết kế.

Agent không sử dụng tài khoản đăng nhập của con người
và không mang ba vai trò RBAC nêu trên.

## 6. Bảng tổng hợp

| Tác nhân | Mục tiêu chính | Kênh tương tác |
|---|---|---|
| Administrator | Quản trị tài khoản, quyền và cấu hình hệ thống | Web Portal |
| Operator | Giám sát hạ tầng và điều phối xử lý sự cố | Web Portal |
| Technician | Kiểm tra thiết bị và thực hiện bảo trì | Mobile AR; Web theo quyền được cấp |
| Collector Agent | Thu thập và gửi dữ liệu vận hành | API hoặc giao thức thu thập theo thiết kế |

## 7. Nguyên tắc truy cập

- Người sử dụng phải đăng nhập trước khi truy cập chức năng được bảo vệ.
- Backend kiểm tra quyền cho từng API.
- Ẩn menu trên giao diện không thay thế việc kiểm tra quyền tại Backend.
- Tài khoản bị vô hiệu hóa không được truy cập API được bảo vệ.
- Quyền thao tác cụ thể được quy định trong ma trận phân quyền.

## 8. Phạm vi tài liệu

Các nhu cầu trên mô tả yêu cầu của hệ thống,
không khẳng định tất cả chức năng đã được triển khai.

Kết quả triển khai được theo dõi trong tài liệu sprint,
báo cáo kiểm thử và mã nguồn tương ứng.
