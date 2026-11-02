# Mục tiêu của dự án AR-IMMS

## 1. Mục đích tài liệu
Tài liệu xác định mục tiêu tổng quát, các mục tiêu cụ thể
và cách đánh giá kết quả của dự án AR-IMMS.

Các mục tiêu được xây dựng từ những vấn đề đã phân tích
trong AI-2, làm cơ sở xác định phạm vi, yêu cầu và kế hoạch
kiểm thử của hệ thống.

## 2. Mục tiêu tổng quát
Xây dựng hệ thống giám sát và bảo trì hạ tầng máy chủ
tích hợp thực tế tăng cường, liên kết vị trí thiết bị vật lý
với dữ liệu vận hành, cảnh báo và công việc bảo trì.

Hệ thống hỗ trợ Operator theo dõi hạ tầng và điều phối
xử lý sự cố, đồng thời cung cấp cho Technician thông tin
theo ngữ cảnh ngay tại thiết bị cần kiểm tra.

Tính khả thi của giải pháp được triển khai và đánh giá
trên Mini Data Center Testbed.

## 3. Các mục tiêu cụ thể
### OBJ-01 Liên kết thiết bị vật lý với tài sản kỹ thuật số
Biểu diễn hạ tầng theo cấu trúc:
Site → Room → Rack → Node/Server → Container/Workload.

Mỗi thiết bị được liên kết với vị trí, thông tin tài sản
và marker nhận diện tương ứng.

**Cách kiểm chứng:**
- Đối chiếu thông tin trên hệ thống với thiết bị trong testbed.
- Kiểm tra quan hệ giữa node, rack và workload.
- Quét marker và xác nhận hệ thống trả về đúng thiết bị.

### OBJ-02 Cung cấp dữ liệu giám sát kịp thời

Thu thập và cung cấp telemetry của server, trạng thái
container và trạng thái kết nối để người dùng theo dõi
hoạt động hạ tầng.

**Tiêu chí đánh giá:**
- Chu kỳ thu thập telemetry mặc định là 5 giây và cấu hình được.
- Node được xác định không khả dụng khi không nhận telemetry
  trong hơn 90 giây.
- Giao diện thể hiện thời điểm cập nhật cuối và dữ liệu cũ.
- Agent tự thử gửi lại và tiếp tục hoạt động sau khi kết nối lại.

### OBJ-03 Hỗ trợ xác định và kiểm tra thiết bị bằng AR

Cung cấp ứng dụng Android nhận diện marker QR/ArUco
đã liên kết với thiết bị và hiển thị thông tin vận hành
trên giao diện camera.

**Cách kiểm chứng:**
- Quét marker trên các thiết bị khác nhau trong testbed.
- Xác nhận overlay hiển thị đúng thông tin của thiết bị được quét.
- Kiểm tra khả năng cập nhật telemetry trong phiên AR.

### OBJ-04 Liên kết cảnh báo với quy trình bảo trì

Hỗ trợ quy trình từ phát hiện bất thường, xác nhận cảnh báo,
tạo và phân công ticket đến ghi nhận kết quả và phê duyệt đóng.

**Cách kiểm chứng:**
- Tạo sự cố có kiểm soát trong testbed.
- Theo dõi luồng cảnh báo → ticket → phân công → xử lý
  → yêu cầu đóng → Operator phê duyệt.
- Kiểm tra khả năng ngăn cảnh báo trùng cho cùng sự cố.
- Kiểm tra việc lưu nguyên nhân, hành động khắc phục
  và kết quả bảo trì.

### OBJ-05 Quản lý lịch sử tài sản và truy vết hoạt động

Lưu thông số phần cứng, thông tin bảo hành, lịch sử bảo trì
và audit log để hỗ trợ quản lý vòng đời tài sản.

**Cách kiểm chứng:**
- Truy xuất lịch sử bảo trì theo thiết bị.
- Kiểm tra thông tin và cảnh báo bảo hành.
- Đối chiếu audit log với thay đổi cấu hình và cập nhật ticket.
- Kiểm tra người dùng thông thường không thể sửa hoặc xóa
  audit log thông qua chức năng được cung cấp.

### OBJ-06 Cung cấp báo cáo phục vụ vận hành

Cung cấp dữ liệu lịch sử và báo cáo theo Site, Room, Rack
và Node để hỗ trợ phân tích xu hướng tài nguyên,
lập kế hoạch công suất và theo dõi hoạt động bảo trì.

**Cách kiểm chứng:**
- Đối chiếu biểu đồ và báo cáo với dữ liệu đã lưu.
- Kiểm tra bộ lọc thời gian và cấp tài sản.
- Với phân tích điện năng/PUE, xác định rõ nguồn dữ liệu,
  đơn vị và khoảng đo.
- Nếu sử dụng dữ liệu mô phỏng, phải ghi rõ trên báo cáo.
- Không suy ra PUE chỉ từ mức sử dụng CPU hoặc RAM.

### OBJ-07 Đảm bảo truy cập có kiểm soát và khả năng mở rộng PoC

Áp dụng xác thực, phân quyền và định danh agent,
đồng thời cho phép bổ sung node mà không sửa code service lõi.

**Tiêu chí đánh giá:**
- Phân quyền theo Administrator, Operator và Technician.
- Agent sử dụng mTLS khi gửi telemetry.
- Node mới bắt đầu streaming và xuất hiện trong Digital Twin
  trong tối đa 5 phút kể từ lúc đăng ký.
- Việc bổ sung node chỉ cần cấu hình credentials
  và endpoint address theo quy trình đã thiết kế.

## 4. Đánh giá hiệu quả hỗ trợ bảo trì

Dự án kỳ vọng giúp kỹ thuật viên xác định đúng thiết bị
và truy cập thông tin chẩn đoán thuận tiện hơn.

Để đánh giá, nhóm thực hiện các kịch bản có thể so sánh:

1. Xác định thiết bị bằng cách đối chiếu thông tin thủ công.
2. Xác định cùng thiết bị bằng ứng dụng AR.
3. Ghi nhận thời gian, độ chính xác và các thao tác tra cứu.
4. Tổng hợp kết quả và phân tích các trường hợp thất bại.

Nếu đánh giá MTTR, cần thống nhất thời điểm bắt đầu,
thời điểm kết thúc và điều kiện thực hiện từng kịch bản.

Không khẳng định mức giảm thời gian hoặc tỷ lệ cải thiện
khi chưa có kết quả thực nghiệm.

## 5. Sản phẩm dự kiến bàn giao
- Mini Data Center Testbed và Collector Agent.
- Backend API và Real-Time Telemetry Engine.
- Next.js Web Management Portal.
- React Native Mobile AR Application trên Android.
- Module cảnh báo, incident và ticket bảo trì.
- Module vòng đời tài sản và audit.
- Báo cáo và phân tích dữ liệu lịch sử.
- Mã nguồn, bộ kiểm thử, script triển khai và tài liệu sử dụng.
## 6. Giới hạn của việc đánh giá
Các mục tiêu được kiểm chứng trong điều kiện testbed.
Kết quả chưa đại diện cho mọi Data Center thực tế.
Số lượng node, thời lượng thử nghiệm, thiết bị Android
và các mức tải kiểm thử phải được nhóm xác định,
ghi nhận trong kế hoạch đánh giá.
Các mục tiêu trong tài liệu là tiêu chí dự kiến,
không phải xác nhận rằng hệ thống đã đạt được.