# Yêu cầu phi chức năng hệ thống AR-IMMS

## 1. Phạm vi áp dụng

Các yêu cầu áp dụng cho Collector Agent, Backend, cơ sở dữ liệu,
Web Management Portal và ứng dụng Mobile AR trên Android.

Việc kiểm chứng được thực hiện trên Mini Data Center Testbed.
Báo cáo phải ghi rõ cấu hình thiết bị, số Node, Workload,
điều kiện mạng và thời lượng thử nghiệm.

Các yêu cầu dưới đây không đồng nghĩa chức năng đã được triển khai.

## 2. Danh sách yêu cầu

| Mã | Nhóm yêu cầu | Nội dung | Cách kiểm chứng |
|---|---|---|---|
| NFR-01 | Chu kỳ telemetry | Collector Agent hỗ trợ chu kỳ thu thập có thể cấu hình, mặc định 5 giây. Chu kỳ thu thập khác với độ trễ truyền đến giao diện. | Kiểm tra cấu hình mặc định, timestamp các mẫu và việc áp dụng chu kỳ mới. |
| NFR-02 | Phát hiện mất kết nối | Xác định Node không khả dụng khi thời gian không nhận telemetry vượt quá 90 giây. | Ngắt telemetry, kiểm tra trước, đúng và sau mốc 90 giây; ghi nhận độ trễ kiểm tra và cập nhật giao diện. |
| NFR-03 | Phục hồi kết nối | Agent tự retry khi gửi thất bại và tiếp tục gửi sau khi kết nối phục hồi. | Ngắt mạng, quan sát retry, khôi phục mạng và xác nhận Backend nhận dữ liệu trở lại. |
| NFR-04 | Độ mới dữ liệu | Phân biệt dữ liệu cũ với dữ liệu hiện tại; hiển thị thời điểm cập nhật cuối. Ngưỡng dữ liệu cũ không mặc định bằng ngưỡng mất kết nối. | Dừng cập nhật hoặc gửi mẫu cũ; kiểm tra trạng thái và thời gian hiển thị. |
| NFR-05 | Cảnh báo trùng | Ngăn tạo nhiều cảnh báo trùng cho cùng sự cố đang hoạt động. | Gửi liên tiếp các mẫu cùng thỏa điều kiện; kiểm tra số cảnh báo và hành vi khi sự cố tái diễn. |
| NFR-06 | Xác thực và phân quyền | Các chức năng được bảo vệ yêu cầu xác thực và kiểm tra quyền tại Backend theo ba vai trò Administrator, Operator, Technician. | Kiểm tra thiếu xác thực, thiếu quyền và đủ quyền trên API cùng kênh dữ liệu thời gian thực. |
| NFR-07 | Bảo mật Agent | Kết nối telemetry giữa Agent và Backend sử dụng mTLS. | Chứng thư hợp lệ kết nối được; thiếu hoặc không tin cậy bị từ chối; Agent kiểm tra chứng thư Backend. |
| NFR-08 | Audit logging | Ghi audit cho thay đổi cấu hình, cập nhật ticket và thao tác từ xa thuộc phạm vi hệ thống. | Đối chiếu thao tác với bản ghi có người hoặc nguồn thực hiện, đối tượng, thời điểm, hành động và kết quả. |
| NFR-09 | Bổ sung Node | Trong PoC, Node mới bắt đầu gửi telemetry và xuất hiện trong Digital Twin trong tối đa 5 phút từ khi hoàn tất đăng ký. Chỉ cần cấu hình credentials và endpoint, không sửa code service lõi. | Đo thời gian đến mẫu đầu tiên và thời điểm xuất hiện trên Digital Twin; kiểm tra không sửa code lõi. |
| NFR-10 | Logging và kiểm thử | Có logging tập trung và kiểm thử tự động cho các luồng quan trọng đã thống nhất. | Tạo lỗi thu thập, truyền và xử lý; tra cứu log, chạy bộ kiểm thử và lưu bằng chứng. |
| NFR-11 | Giao diện và nền tảng | Web ưu tiên máy tính, sử dụng tiếng Anh, responsive và hỗ trợ khả năng truy cập. Mobile AR chạy trên Android. Trạng thái không chỉ được biểu diễn bằng màu. | Kiểm tra ngôn ngữ, bố cục, nhãn điều khiển, bàn phím và thiết bị Android đã chọn. |
| NFR-12 | Vòng đời sự cố | Incident tuân theo Open → In-progress → Resolved → Closed; chuyển trạng thái phải kiểm tra quyền và ghi audit. Operator phê duyệt đóng theo quy trình ticket. Vòng đời cảnh báo được đặc tả riêng. | Kiểm tra chuyển trạng thái hợp lệ, sai trình tự, thiếu quyền và bước phê duyệt đóng. |
| NFR-13 | Khả năng cấu hình | Metric giám sát và ngưỡng cảnh báo có thể cấu hình, không phụ thuộc hoàn toàn vào giá trị cố định trong mã nguồn. | Thay đổi cấu hình bằng quyền phù hợp; xác nhận cấu hình có hiệu lực và có audit. |
| NFR-14 | Tính sẵn sàng | Hệ thống hoạt động trong khung giờ testbed đã thống nhất; thông báo khi server hoặc Collector không khả dụng. Chưa đặt cam kết uptime khi chưa có căn cứ. | Chạy trong khung giờ thử nghiệm, gây gián đoạn và ghi nhận thời gian cùng ảnh hưởng. |
| NFR-15 | Thao tác từ xa | Nếu có thao tác gây gián đoạn trong phiên AR, phải kiểm tra quyền, yêu cầu xác nhận và ghi audit. Yêu cầu này không tự bổ sung chức năng điều khiển từ xa vào phạm vi. | Hủy xác nhận không thực thi; người thiếu quyền bị từ chối; kết quả thực thi có audit. |
| NFR-16 | Toàn vẹn audit | Bảo vệ audit log khỏi sửa hoặc xóa qua chức năng và API của ứng dụng. | Kiểm tra quyền API và kho lưu audit; xác nhận các vai trò không thể sửa, xóa trái phép. |
| NFR-17 | Toàn vẹn telemetry | Mỗi bản ghi liên kết đúng Node và có thời điểm thu thập. | Gửi mẫu hợp lệ và mẫu thiếu định danh hoặc thời gian; kiểm tra kết quả lưu và xử lý lỗi. |
| NFR-18 | Telemetry trùng | Nhận diện và xử lý mẫu telemetry trùng theo chính sách thống nhất. Đây là yêu cầu riêng với chống cảnh báo trùng. | Gửi lại cùng mẫu nhiều lần, đối chiếu số bản ghi và kết quả xử lý. |
| NFR-19 | Bảo vệ mật khẩu | Không lưu mật khẩu người sử dụng dưới dạng văn bản thuần; API và log không làm lộ mật khẩu hoặc password hash. | Kiểm tra cơ chế hash, dữ liệu lưu, phản hồi API và log. |

## 3. Các thông số cần thống nhất trước nghiệm thu

| Yêu cầu | Nội dung cần chốt |
|---|---|
| NFR-02 | Tần suất kiểm tra và độ trễ phát hiện cho phép. |
| NFR-03 | Số lần retry, khoảng chờ, giới hạn bộ đệm và cách xử lý dữ liệu chưa gửi. |
| NFR-04 | Ngưỡng và quy tắc xác định dữ liệu cũ. |
| NFR-05 | Khóa nhận diện sự cố, điều kiện phục hồi và quy tắc tái mở. |
| NFR-10 | Danh sách luồng kiểm thử và tiêu chí bao phủ. |
| NFR-11 | Trình duyệt, kích thước màn hình, thiết bị Android và tiêu chí khả năng truy cập. |
| NFR-14 | Khung giờ và thời lượng thử nghiệm. |
| NFR-16 | Cơ chế bảo vệ tầng lưu trữ và chính sách lưu giữ audit. |
| NFR-18 | Khóa nhận diện mẫu trùng và chính sách xử lý. |

Các thông số chưa chốt phải được ghi nhận bằng quyết định của nhóm,
không mặc định coi là đã đáp ứng.

## 4. Lưu ý về chu kỳ telemetry

Yêu cầu hiện tại sử dụng chu kỳ thu thập mặc định 5 giây
và ngưỡng không nhận telemetry lớn hơn 90 giây.

Nếu nhóm đổi sang thu thập hoặc gửi mỗi 5 phút,
phải rà soát đồng thời:

- NFR-01: chu kỳ thu thập và chu kỳ gửi.
- NFR-02: cách phát hiện Node không khả dụng.
- NFR-04: ngưỡng dữ liệu cũ.
- NFR-09: thời gian tiếp nhận Node mới.
- Cách mô tả cập nhật thời gian thực trên giao diện.

Có thể sử dụng heartbeat riêng để theo dõi kết nối
nếu telemetry được gửi với chu kỳ dài.

## 5. Bằng chứng nghiệm thu

Mỗi yêu cầu cần có ca kiểm thử hoặc phương pháp kiểm chứng,
kết quả thực tế và thông tin môi trường.

Không đánh dấu đạt chỉ dựa trên mô tả thiết kế
hoặc việc ứng dụng build thành công.