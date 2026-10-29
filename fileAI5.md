AI-5: XÁC ĐỊNH CÁC TÁC NHÂN CỦA HỆ THỐNG AR-IMMS
## 1. Mục tiêu
Xác định các tác nhân tương tác với hệ thống AR-IMMS, làm rõ vai trò và trách nhiệm của từng tác nhân trong quá trình quản lý, giám sát và bảo trì Mini Data Center Testbed.
## 2. Nội dung thực hiện
Xác định các tác nhân chính của hệ thống AR-IMMS và mô tả vai trò, chức năng của từng tác nhân, bao gồm:
- **System Administrator (Quản trị viên hệ thống)**: quản lý tài khoản người dùng, phân quyền, cấu hình hệ thống; theo dõi tình trạng dịch vụ và data collector; quản lý môi trường thử nghiệm, xem audit log và lịch sử thay đổi cấu hình.
- **System Operator (Nhân viên vận hành hệ thống)**: quản lý rack, server, workload và liên kết QR/ArUco; theo dõi telemetry và Digital Twin; cấu hình, xác nhận cảnh báo; tạo, phân công và theo dõi incident/maintenance ticket; quản lý tài sản và xem báo cáo vận hành.
- **Technician (Kỹ thuật viên)**: xem ticket được giao, xác định rack/server cần kiểm tra, quét QR/ArUco bằng ứng dụng AR; xem telemetry, cảnh báo và thông tin chẩn đoán; cập nhật tiến độ, ghi nhận nguyên nhân, biện pháp khắc phục và kết quả bảo trì.
- **Automated Monitoring and Alerting System (Hệ thống giám sát và cảnh báo tự động)**: thu thập telemetry và trạng thái kết nối; phát hiện server không khả dụng hoặc chỉ số vượt ngưỡng; tạo/cập nhật cảnh báo, lưu telemetry lịch sử và ghi lại hoạt động quan trọng vào audit log.
Xác định mối quan hệ và giới hạn tương tác của các tác nhân với chức năng hệ thống, phù hợp với cơ chế xác thực và phân quyền theo vai trò (RBAC).
## 3. Phạm vi xác định tác nhân
Phạm vi gồm ba nhóm người dùng chính: System Administrator, System Operator và Technician; cùng tác nhân tự động Automated Monitoring and Alerting System. Các tác nhân tương tác với hệ thống trong môi trường Mini Data Center Testbed để quản trị, vận hành, giám sát, cảnh báo và thực hiện bảo trì.
## 4. Kết quả bàn giao
Tài liệu mô tả 4 tác nhân của hệ thống AR-IMMS, bao gồm:
Tên và mục đích của từng tác nhân.
Vai trò, trách nhiệm và các chức năng tương ứng.
Mối quan hệ giữa tác nhân với các chức năng giám sát, cảnh báo, quản lý tài sản, ticket và bảo trì.
Thông tin làm cơ sở xây dựng sơ đồ Use Case và đặc tả yêu cầu hệ thống.
## 5. Tiêu chí đánh giá
Tài liệu được đánh giá dựa trên việc xác định đầy đủ 4 tác nhân; mô tả rõ vai trò và trách nhiệm của từng tác nhân; phân biệt đúng quyền quản trị, vận hành và xử lý bảo trì; bảo đảm nội dung phù hợp với yêu cầu AR-IMMS và cơ chế phân quyền RBAC.
## 6. Kết luận
Việc xác định các tác nhân giúp làm rõ những đối tượng tương tác với hệ thống AR-IMMS và trách nhiệm của từng đối tượng. Đây là cơ sở để thiết kế chức năng, phân quyền và xây dựng sơ đồ Use Case cho hệ thống.