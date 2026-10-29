# Phân tích bối cảnh và vấn đề của hệ thống AR-IMMS

##  Mục đích,Bối cảnh vận hành
Tài liệu phân tích bối cảnh giám sát và bảo trì hạ tầng máy chủ,
xác định những khó khăn khi dữ liệu vận hành tách biệt với vị trí
thiết bị vật lý, từ đó làm rõ nhu cầu xây dựng AR-IMMS.
Kết quả phân tích là đầu vào để xác định mục tiêu dự án,
phạm vi, tác nhân và yêu cầu hệ thống ở các tài liệu tiếp theo.

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
---

## 7. Kế hoạch triển khai và kiểm thử tích hợp

Để đảm bảo các mục tiêu của dự án AR-IMMS được hiện thực hóa đúng tiến độ và đạt các tiêu chí kiểm chứng đã đề ra, kế hoạch thực hiện được chia thành các giai đoạn chính:

### 7.1. Giai đoạn 1: Chuẩn bị hạ tầng Testbed và Collector Agent
* **Thiết lập phần cứng & mạng:** Cấu hình các máy tính vật lý làm node/server, thiết lập nhóm rack và kết nối mạng nội bộ cho Mini Data Center.
* **Phát triển Collector Agent:** Xây dựng script/chương trình chạy trên các node để định kỳ thu thập các chỉ số telemetry (CPU, RAM, Network, Disk) với chu kỳ mặc định 5 giây.
* **Cơ chế bảo mật agent:** Tích hợp xác thực mTLS giữa Collector Agent và Backend để đảm bảo an toàn truyền dữ liệu.

### 7.2. Giai đoạn 2: Xây dựng Backend Core & Digital Twin Engine
* **Xây dựng mô hình cơ sở dữ liệu:** Thiết kế cấu trúc phân cấp tài sản từ `Site → Room → Rack → Node/Server → Container/Workload`.
* **Xử lý Real-Time Telemetry:** Phát triển engine tiếp nhận dữ liệu, xử lý trạng thái kết nối (đánh dấu node không khả dụng nếu mất tín hiệu trên 90 giây) và cơ chế tự kết nối lại của agent.
* **Module phân quyền RBAC:** Triển khai cơ chế phân định rõ quyền hạn cho 3 nhóm người dùng: *System Administrator*, *System Operator* và *Technician*.

### 7.3. Giao đoạn 3: Phát triển Web Management Portal & Mobile AR App
* **Web Portal (Next.js):** Xây dựng giao diện trực quan giúp Operator và Administrator giám sát trạng thái hệ thống, quản lý sơ đồ Digital Twin, tiếp nhận cảnh báo và phân công ticket.
* **Mobile AR App (React Native - Android):** Phát triển ứng dụng trên thiết bị di động Android tích hợp thư viện quét marker QR/ArUco, hiển thị thông tin dạng overlay theo ngữ cảnh thiết bị tại hiện trường.
* **Module Cảnh báo & Ticket:** Hoàn thiện luồng tự động chuyển đổi cảnh báo thành ticket, ngăn chặn việc tạo trùng lặp cảnh báo cho cùng một sự cố, đồng thời ghi nhận nhật ký bảo trì và audit log.

### 7.4. Giai đoạn 4: Kiểm thử, Đánh giá và Hoàn thiện tài liệu
* **Kiểm thử tích hợp hệ thống:** Chạy thử nghiệm toàn bộ luồng từ lúc phát sinh bất thường, tạo ticket, kỹ thuật viên quét mã AR xử lý cho đến khi Operator phê duyệt đóng ticket.
* **Đánh giá thực nghiệm:** Thực hiện các kịch bản so sánh thời gian và độ chính xác giữa phương pháp đối chiếu thủ công và sử dụng ứng dụng AR.
* **Đóng gói sản phẩm:** Hoàn thiện mã nguồn, kịch bản test, script triển khai tự động và bộ tài liệu hướng dẫn sử dụng chi tiết bàn giao cho hội đồng đánh giá.

## .8  XÁC ĐỊNH CÁC TÁC NHÂN CỦA HỆ THỐNG AR-IMMS

## 8.1 Mục tiêu
Xác định các tác nhân tương tác với hệ thống AR-IMMS, làm rõ vai trò và trách nhiệm của từng tác nhân trong quá trình quản lý, giám sát và bảo trì Mini Data Center Testbed.

## 8.2 Nội dung thực hiện
Xác định các tác nhân chính của hệ thống AR-IMMS và mô tả vai trò, chức năng của từng tác nhân, bao gồm:
- **System Administrator (Quản trị viên hệ thống)**: quản lý tài khoản người dùng, phân quyền, cấu hình hệ thống; theo dõi tình trạng dịch vụ và data collector; quản lý môi trường thử nghiệm, xem audit log và lịch sử thay đổi cấu hình.
- **System Operator (Nhân viên vận hành hệ thống)**: quản lý rack, server, workload và liên kết QR/ArUco; theo dõi telemetry và Digital Twin; cấu hình, xác nhận cảnh báo; tạo, phân công và theo dõi incident/maintenance ticket; quản lý tài sản và xem báo cáo vận hành.
- **Technician (Kỹ thuật viên)**: xem ticket được giao, xác định rack/server cần kiểm tra, quét QR/ArUco bằng ứng dụng AR; xem telemetry, cảnh báo và thông tin chẩn đoán; cập nhật tiến độ, ghi nhận nguyên nhân, biện pháp khắc phục và kết quả bảo trì.
- **Automated Monitoring and Alerting System (Hệ thống giám sát và cảnh báo tự động)**: thu thập telemetry và trạng thái kết nối; phát hiện server không khả dụng hoặc chỉ số vượt ngưỡng; tạo/cập nhật cảnh báo, lưu telemetry lịch sử và ghi lại hoạt động quan trọng vào audit log.
Xác định mối quan hệ và giới hạn tương tác của các tác nhân với chức năng hệ thống, phù hợp với cơ chế xác thực và phân quyền theo vai trò (RBAC).

## 8.3 Phạm vi xác định tác nhân
Phạm vi gồm ba nhóm người dùng chính: System Administrator, System Operator và Technician; cùng tác nhân tự động Automated Monitoring and Alerting System. Các tác nhân tương tác với hệ thống trong môi trường Mini Data Center Testbed để quản trị, vận hành, giám sát, cảnh báo và thực hiện bảo trì.

## 8.4 Kết quả bàn giao
Tài liệu mô tả 4 tác nhân của hệ thống AR-IMMS, bao gồm:
Tên và mục đích của từng tác nhân.
Vai trò, trách nhiệm và các chức năng tương ứng.
Mối quan hệ giữa tác nhân với các chức năng giám sát, cảnh báo, quản lý tài sản, ticket và bảo trì.
Thông tin làm cơ sở xây dựng sơ đồ Use Case và đặc tả yêu cầu hệ thống.

## 8.5 Tiêu chí đánh giá
Tài liệu được đánh giá dựa trên việc xác định đầy đủ 4 tác nhân; mô tả rõ vai trò và trách nhiệm của từng tác nhân; phân biệt đúng quyền quản trị, vận hành và xử lý bảo trì; bảo đảm nội dung phù hợp với yêu cầu AR-IMMS và cơ chế phân quyền RBAC.

## 8.6 Kết luận
Việc xác định các tác nhân giúp làm rõ những đối tượng tương tác với hệ thống AR-IMMS và trách nhiệm của từng đối tượng. Đây là cơ sở để thiết kế chức năng, phân quyền và xây dựng sơ đồ Use Case cho hệ thống.
