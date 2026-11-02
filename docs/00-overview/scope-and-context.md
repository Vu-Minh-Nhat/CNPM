# Phạm vi hệ thống và sơ đồ ngữ cảnh AR-IMMS

## 1. Mục đích

Xác định phạm vi của hệ thống AR-IMMS, môi trường hoạt động
và các tương tác giữa hệ thống với người sử dụng, Collector Agent.

## 2. Phạm vi hệ thống

AR-IMMS hỗ trợ quản lý, giám sát và bảo trì hạ tầng trong
Mini Data Center Testbed.

Các nhóm chức năng dự kiến gồm:

- Đăng nhập, xác thực và phân quyền người sử dụng.
- Quản lý cấu trúc tài sản: Site, Room, Rack, Node và Workload.
- Thu thập, lưu trữ và hiển thị telemetry.
- Phát hiện và quản lý cảnh báo.
- Tạo, phân công và theo dõi ticket xử lý sự cố hoặc bảo trì.
- Tra cứu tài sản và hỗ trợ kiểm tra thiết bị bằng Mobile AR.
- Quản lý lịch sử bảo trì và audit log.
- Cung cấp thông tin tổng hợp phục vụ vận hành.

Danh sách trên mô tả phạm vi yêu cầu của dự án.
Trạng thái triển khai được theo dõi trong tài liệu sprint và kiểm thử.

## 3. Môi trường hoạt động

| Thành phần | Mô tả |
|---|---|
| Web Management Portal | Truy cập bằng trình duyệt, phục vụ quản trị và vận hành |
| Mobile AR | Ứng dụng Android phục vụ Technician tại hiện trường |
| Backend | NestJS, cung cấp API và xử lý nghiệp vụ |
| Web Frontend | Next.js |
| Mobile Application | React Native, tích hợp khả năng AR theo thiết kế |
| Truyền dữ liệu thời gian thực | Socket.IO |
| Cơ sở dữ liệu | PostgreSQL cho dữ liệu nghiệp vụ; cách lưu telemetry được xác định trong thiết kế dữ liệu |
| Môi trường thử nghiệm | Máy tính vật lý đại diện cho server, container đại diện cho workload |

Agent, Backend, Web và Mobile cần kết nối mạng để trao đổi dữ liệu.

Khi mất kết nối, hệ thống phải thể hiện rõ trạng thái
và thời điểm cập nhật cuối của dữ liệu liên quan.

## 4. Tác nhân và hệ thống bên ngoài

| Tác nhân | Vai trò |
|---|---|
| System Administrator | Quản lý tài khoản, phân quyền, cấu hình, sức khỏe hệ thống và audit log |
| System Operator | Quản lý tài sản, giám sát telemetry, xử lý cảnh báo, phân công và phê duyệt đóng ticket |
| Technician | Nhận công việc, nhận diện thiết bị qua marker và cập nhật kết quả bảo trì |
| Collector Agent | Thu thập và gửi telemetry, trạng thái kết nối về hệ thống |

Collector Agent được biểu diễn là thành phần bên ngoài
ranh giới Web, Mobile và Backend trong sơ đồ ngữ cảnh này.

## 5. Các tương tác trong sơ đồ ngữ cảnh

| Tác nhân | Dữ liệu hoặc yêu cầu gửi đến AR-IMMS | Thông tin nhận từ AR-IMMS |
|---|---|---|
| Administrator | Yêu cầu quản lý tài khoản, phân quyền và cấu hình | Kết quả thao tác, thông tin cấu hình, sức khỏe hệ thống và audit log |
| Operator | Yêu cầu quản lý tài sản, cấu hình cảnh báo và phân công ticket | Thông tin tài sản, telemetry, cảnh báo, ticket và báo cáo |
| Technician | Thông tin marker, yêu cầu tra cứu và kết quả bảo trì | Thông tin thiết bị, telemetry và ticket được giao |
| Collector Agent | Telemetry và trạng thái kết nối | Cấu hình thu thập theo cơ chế được thống nhất trong thiết kế |

## 6. Sơ đồ ngữ cảnh

![Sơ đồ ngữ cảnh AR-IMMS](docs/srs/images/sodongucanh.png)

Sơ đồ thể hiện AR-IMMS như một hệ thống tổng thể
và mô tả các luồng trao đổi với tác nhân bên ngoài.

Chi tiết bảng dữ liệu, API và thành phần nội bộ được trình bày
trong các tài liệu thiết kế tương ứng.

## 7. Giới hạn và giả định

- Hệ thống được triển khai và đánh giá trong Mini Data Center Testbed.
- Kết quả thử nghiệm được xem xét theo quy mô và điều kiện testbed.
- Khả năng nhận diện AR phụ thuộc vào camera, marker,
  ánh sáng và thiết bị Android sử dụng.
- Việc thu thập telemetry phụ thuộc vào Collector Agent
  và khả năng kết nối đến backend.
- Chức năng điều khiển từ xa hoặc tự động can thiệp thiết bị
  chỉ được triển khai khi có yêu cầu và quy tắc nghiệp vụ rõ ràng.

## 8. Tài liệu liên quan

- [Bối cảnh và vấn đề cần giải quyết](01-project-background.md)
- [Mục tiêu dự án](02-project-objectives.md)
- [Các khái niệm chính](03-core-domain-concepts.md)