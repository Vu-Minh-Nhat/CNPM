# Phân tích bối cảnh và vấn đề của hệ thống AR-IMMS

##  Mục đích
Tài liệu phân tích bối cảnh giám sát và bảo trì hạ tầng máy chủ,
xác định những khó khăn khi dữ liệu vận hành tách biệt với vị trí
thiết bị vật lý, từ đó làm rõ nhu cầu xây dựng AR-IMMS.

Kết quả phân tích là đầu vào để xác định mục tiêu dự án,
phạm vi, tác nhân và yêu cầu hệ thống ở các tài liệu tiếp theo.

##  Bối cảnh vận hành
Trong Data Center và Server Room, các máy chủ được bố trí
trong nhiều rack và có thể có hình thức bên ngoài tương tự nhau.
Mỗi máy chủ có thể chạy nhiều ứng dụng, service hoặc container.

Nhân viên vận hành theo dõi các chỉ số như CPU, RAM, lưu lượng
mạng và trạng thái dịch vụ thông qua dashboard và công cụ
giám sát tập trung.

Dashboard cung cấp thông tin vận hành nhưng kỹ thuật viên
vẫn cần xác định thiết bị tương ứng tại hiện trường.
Việc liên kết giữa thông tin số và vị trí phần cứng là vấn đề
trọng tâm mà AR-IMMS hướng tới giải quyết.

##  Quy trình xử lý sự cố làm cơ sở phân tích
Quy trình dưới đây được mô tả theo bối cảnh của đề tài,
cần được xác nhận thêm khi khảo sát người sử dụng.

1. Hệ thống giám sát phát hiện chỉ số bất thường hoặc mất kết nối.
2. Nhân viên vận hành kiểm tra cảnh báo và thông tin thiết bị.
3. Nhân viên vận hành xác định vị trí và giao việc kiểm tra.
4. Kỹ thuật viên đối chiếu thông tin để tìm rack và máy chủ.
5. Kỹ thuật viên tra cứu telemetry, log và lịch sử bảo trì.
6. Kỹ thuật viên kiểm tra, xử lý và ghi nhận kết quả.
7. Nhân viên vận hành kiểm tra kết quả và xác nhận hoàn tất.

Các bước xác định thiết bị và tra cứu thông tin có thể yêu cầu
chuyển đổi giữa dashboard, sơ đồ vị trí và hồ sơ bảo trì.

##  Các vấn đề cần giải quyết
| Mã | Vấn đề | Nguyên nhân trong bối cảnh đề tài | Ảnh hưởng có thể xảy ra |
|---|---|---|---|
| P-01 | Khó xác định đúng thiết bị tại hiện trường | Thông tin cảnh báo chưa liên kết trực quan với vị trí vật lý | Tốn thời gian đối chiếu, có nguy cơ kiểm tra nhầm thiết bị |
| P-02 | Thiếu thông tin chẩn đoán ngay tại thiết bị | Telemetry, workload, log và lịch sử bảo trì nằm ở các giao diện hoặc hồ sơ riêng | Kỹ thuật viên phải tra cứu nhiều nơi |
| P-03 | Quy trình xử lý sự cố thiếu liên kết | Cảnh báo, thiết bị và công việc bảo trì chưa được kết nối xuyên suốt | Khó theo dõi người xử lý, tiến độ và kết quả |
| P-04 | Khó truy vết hoạt động bảo trì | Các thay đổi và kết quả xử lý chưa được ghi nhận thống nhất | Khó kiểm tra lịch sử và tổng hợp báo cáo |

Đây là các vấn đề được xác định từ đề tài.
Mức độ ảnh hưởng thực tế cần được kiểm chứng khi đánh giá testbed.

##  Nhu cầu của các bên sử dụng
| Bên sử dụng | Nhu cầu chính |
|---|---|
| System Administrator | Quản lý tài khoản, quyền truy cập, cấu hình và sức khỏe hệ thống |
| System Operator | Theo dõi hạ tầng theo vị trí, kiểm tra cảnh báo, giao và theo dõi ticket |
| Technician | Nhận diện đúng thiết bị, xem thông tin tại hiện trường và cập nhật kết quả bảo trì |

Ma trận quyền chi tiết được trình bày trong tài liệu AI-5.

##  Định hướng giải pháp
AR-IMMS kết nối tài sản vật lý, dữ liệu vận hành, cảnh báo
và quy trình bảo trì trong cùng một nền tảng.

###  Liên kết tài sản bằng Digital Twin
Mô hình hóa hạ tầng theo cấu trúc:

Site → Room → Rack → Node/Server → Container/Workload.

Cấu trúc này cung cấp thông tin về vị trí và quan hệ giữa
thiết bị với workload đang chạy.

###  Cung cấp dữ liệu vận hành theo thời gian thực
Collector Agent thu thập telemetry từ máy chủ và gửi về backend.
Web Portal và Mobile AR cung cấp dữ liệu liên quan tới thiết bị,
đồng thời thể hiện rõ khi dữ liệu đã cũ hoặc kết nối bị gián đoạn.

###  Cung cấp thông tin theo ngữ cảnh bằng AR
Marker được liên kết với định danh thiết bị.
Kỹ thuật viên dùng điện thoại Android nhận diện marker để
truy cập trạng thái, telemetry, cảnh báo và thông tin bảo trì
của đúng thiết bị tại hiện trường.

###  Liên kết cảnh báo với công việc bảo trì
Cảnh báo được liên kết với tài sản và ticket.
Operator giao công việc; Technician ghi nhận quá trình xử lý,
nguyên nhân và kết quả; Operator phê duyệt đóng ticket.

##  Môi trường triển khai và giới hạn đánh giá
Dự án được triển khai trên Mini Data Center Testbed.

- Các máy tính vật lý đại diện cho node/server.
- Nhóm thiết bị đại diện cho rack.
- Ứng dụng hoặc container đại diện cho workload.
- Marker được gắn lên thiết bị để thử nghiệm nhận diện.

Kết quả đánh giá phản ánh điều kiện của testbed.
Việc áp dụng cho Data Center thực tế cần được đánh giá thêm
về quy mô, môi trường vận hành và yêu cầu bảo mật.

##  Lợi ích kỳ vọng và cách đánh giá
| Lợi ích kỳ vọng | Hướng đánh giá |
|---|---|
| Xác định thiết bị thuận tiện hơn | So sánh thời gian và độ chính xác khi tìm thiết bị bằng đối chiếu thủ công và bằng AR |
| Giảm thao tác tra cứu thông tin | Ghi nhận số bước và thời gian truy cập telemetry, log, lịch sử bảo trì |
| Theo dõi công việc bảo trì rõ ràng hơn | Kiểm tra khả năng truy vết từ cảnh báo đến ticket và kết quả xử lý |

Chưa kết luận hệ thống giảm MTTR khi chưa có kết quả thực nghiệm.
Nếu đánh giá MTTR, cần xác định rõ thời điểm bắt đầu, kết thúc
và sử dụng các kịch bản sự cố có thể so sánh.
