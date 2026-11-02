# Các khái niệm chính trong AR-IMMS

## 1. Mục đích

Thống nhất cách hiểu các thuật ngữ được sử dụng trong tài liệu,
mã nguồn và quá trình vận hành hệ thống AR-IMMS.

## 2. Cấu trúc hạ tầng

Hệ thống tổ chức tài sản theo cấu trúc:

Site → Room → Rack → Node → Workload

| Khái niệm | Ý nghĩa | Ví dụ |
|---|---|---|
| Site | Địa điểm triển khai hạ tầng, gồm nhiều phòng | Mini Data Center Testbed |
| Room | Phòng hoặc khu vực chứa các tủ rack, thuộc một Site | Phòng máy số 1 |
| Rack | Tủ chứa thiết bị, thuộc một Room | Rack R01 |
| Node / Server | Máy chủ hoặc máy tính vật lý, thuộc một Rack | Máy chủ SERVER-01 |
| Workload | Thành phần phần mềm chạy trên một Node | Container chạy ứng dụng thử nghiệm |

Trong phạm vi testbed, máy tính vật lý đại diện cho server;
container đại diện cho workload.

Container là một cách triển khai workload. Hai thuật ngữ này
không hoàn toàn đồng nghĩa.

## 3. Giám sát và dữ liệu vận hành

| Khái niệm | Ý nghĩa |
|---|---|
| Collector Agent | Thành phần thu thập và gửi dữ liệu từ thiết bị về backend |
| Telemetry | Dữ liệu vận hành có thời điểm ghi nhận, ví dụ CPU, RAM và lưu lượng mạng |
| Trạng thái kết nối | Thông tin cho biết thiết bị hoặc Agent còn liên lạc được với hệ thống hay không |
| Alert | Cảnh báo được tạo khi dữ liệu hoặc trạng thái thỏa điều kiện đã cấu hình |
| Dashboard | Giao diện tổng hợp trạng thái tài sản, telemetry và cảnh báo |

Khi mất kết nối, giao diện cần thể hiện trạng thái và thời điểm
cập nhật cuối để người sử dụng nhận biết dữ liệu có thể đã cũ.

## 4. AR và tài sản kỹ thuật số

| Khái niệm | Ý nghĩa |
|---|---|
| Digital Twin | Biểu diễn kỹ thuật số của tài sản, liên kết thông tin định danh, vị trí, telemetry và lịch sử liên quan |
| Marker | Dấu nhận diện vật lý gắn với tài sản, ví dụ QR Code hoặc ArUco theo thiết kế |
| Mobile AR | Ứng dụng di động hỗ trợ nhận diện tài sản và hiển thị thông tin trong ngữ cảnh quan sát thực tế |

Trong phạm vi dự án, Digital Twin tập trung vào thông tin
và trạng thái vận hành của tài sản. Mô hình mô phỏng vật lý
không phải là yêu cầu mặc định của khái niệm này.

## 5. Công việc và truy vết

| Khái niệm | Ý nghĩa |
|---|---|
| Ticket | Bản ghi công việc xử lý sự cố hoặc bảo trì, có người phụ trách và trạng thái |
| Lịch sử bảo trì | Thông tin các lần kiểm tra, sửa chữa và kết quả thực hiện trên tài sản |
| Audit Log | Nhật ký ghi nhận người thực hiện, hành động và thời điểm thao tác |

Alert phản ánh một điều kiện cần chú ý.
Ticket dùng để theo dõi công việc xử lý.
Việc tạo ticket từ alert tuân theo quy tắc nghiệp vụ đã thống nhất.

## 6. Môi trường thử nghiệm

| Khái niệm | Ý nghĩa |
|---|---|
| Testbed | Môi trường thử nghiệm được xây dựng để triển khai và đánh giá hệ thống |
| PoC — Proof of Concept | Bản triển khai nhằm chứng minh tính khả thi của giải pháp trong phạm vi giới hạn |

Kết quả trên Mini Data Center Testbed được đánh giá theo
quy mô và điều kiện thử nghiệm, không tự động đại diện
cho khả năng vận hành tại trung tâm dữ liệu thực tế.

## 7. Ví dụ vận hành

1. Máy chủ SERVER-01 thuộc Rack R01, trong Room 01 của Site thử nghiệm.
2. Collector Agent gửi telemetry của máy chủ về backend.
3. Hệ thống phát hiện dữ liệu vượt ngưỡng đã cấu hình và tạo alert.
4. Operator xem cảnh báo, tạo hoặc phân công ticket theo quy trình.
5. Technician nhận ticket và quét marker để xác định máy chủ.
6. Technician kiểm tra thiết bị và cập nhật kết quả xử lý.
7. Operator kiểm tra kết quả và phê duyệt đóng ticket theo quy trình.

Ví dụ này mô tả luồng nghiệp vụ dự kiến;
không khẳng định mọi chức năng đã được triển khai.