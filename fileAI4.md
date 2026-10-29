# AI-4: XÁC ĐỊNH PHẠM VI DỰ ÁN AR-IMMS
## 1. Mục tiêu
Xác định phạm vi và giới hạn triển khai của hệ thống **AR-IMMS** trên *Mini Data Center Testbed*, làm rõ các hạng mục sẽ thực hiện và kết quả cần bàn giao.
---
## 2. Nội dung thực hiện
Dự án tập trung xây dựng mô hình thử nghiệm giám sát và bảo trì hạ tầng Data Center, bao gồm các nội dung chính sau:
* **Thiết lập Mini Data Center Testbed:** các máy tính vật lý đại diện cho server, nhóm thiết bị đại diện cho rack và ứng dụng/service đại diện cho workload.
* **Xây dựng Backend:** quản lý tài sản, tiếp nhận dữ liệu giám sát và cung cấp API cho các ứng dụng.
* **Thu thập & Hiển thị Telemetry:** thu thập dữ liệu theo thời gian thực như trạng thái server, CPU, RAM và dữ liệu vận hành có sẵn.
* **Xây dựng Web Management Portal:** quản lý rack, server, workload, cảnh báo và thông tin tài sản.
* **Xây dựng ứng dụng Mobile AR:** cho phép quét QR Code hoặc marker ArUco để xem thông tin thiết bị tại hiện trường.
* **Quản lý Incident/Maintenance Ticket:** hỗ trợ tạo, theo dõi và phân công ticket; ghi nhận lịch sử bảo trì và audit log.
* **Kiểm thử:** đánh giá khả năng tích hợp, giám sát, cảnh báo, phân quyền và nhận diện thiết bị trong môi trường thử nghiệm.
---
## 3. Phạm vi hệ thống
Phạm vi hệ thống bao gồm:
* Mini Data Center Testbed
* Collector Agent thu thập dữ liệu
* Backend & Cơ sở dữ liệu
* Luồng Telemetry thời gian thực
* Web Management Portal
* Ứng dụng Mobile AR
**Hệ thống hỗ trợ 03 nhóm người dùng chính:**
1. **Admin**
2. **Operator**
3. **Technician**
---
## 4. Giới hạn triển khai
Dự án được triển khai và đánh giá trong môi trường **Mini Data Center Testbed**, không triển khai trực tiếp lên Data Center đang vận hành thực tế.
* Phạm vi giám sát phụ thuộc vào thiết bị, hệ điều hành, quyền truy cập và dữ liệu có thể thu thập trong testbed.
* **Không bao gồm** việc thay thế hệ thống giám sát đang sử dụng tại Data Center thực tế.
* **Không cam kết** hỗ trợ mọi loại server, thiết bị hoặc nền tảng chưa được lựa chọn cho testbed.
* **Không thực hiện** thao tác có khả năng gây gián đoạn dịch vụ nếu chưa có xác nhận phù hợp.
* Phân tích điện năng/PUE chỉ được thực hiện khi môi trường thử nghiệm có dữ liệu đầu vào cần thiết.
---
## 5. Kết quả bàn giao
Các sản phẩm dự kiến bàn giao gồm:
1. Mô hình Mini Data Center Testbed và Collector Agent.
2. Backend API và hệ thống truyền Telemetry thời gian thực.
3. Web Management Portal phục vụ giám sát và quản lý hạ tầng.
4. Ứng dụng Mobile AR hỗ trợ quét QR/ArUco và tra cứu thông tin thiết bị.
5. Chức năng cảnh báo, quản lý sự cố/ticket, quản lý tài sản và audit log.
6. Mã nguồn, tài liệu kiến trúc, hướng dẫn sử dụng, script triển khai và kết quả kiểm thử.
---
## 6. Tiêu chí đánh giá
Phạm vi dự án được đánh giá dựa trên:
* Khả năng quản lý tài sản theo cấu trúc phân cấp.
* Thu thập và hiển thị dữ liệu telemetry.
* Phát hiện cảnh báo theo ngưỡng cấu hình.
* Tạo và theo dõi ticket xử lý sự cố.
* Nhận diện marker QR/ArUco và hiển thị đúng thông tin thiết bị.
* Hoạt động của cơ chế xác thực, phân quyền và audit log.
> *Tất cả các chức năng được kiểm thử trong môi trường Mini Data Center Testbed.*
---
## 7. Kết luận
Phạm vi trên xác định các thành phần và chức năng chính sẽ được phát triển, kiểm thử và bàn giao cho dự án AR-IMMS. Việc giới hạn triển khai trong Mini Data Center Testbed giúp nhóm đánh giá tính khả thi của giải pháp trước khi xem xét mở rộng sang môi trường thực tế.