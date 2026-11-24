# Quy tắc nghiệp vụ hệ thống AR-IMMS

Các quy tắc dưới đây là yêu cầu của hệ thống.
Trạng thái triển khai được xác nhận qua mã nguồn và kiểm thử.

| Mã | Nhóm | Quy tắc nghiệp vụ |
|---|---|---|
| BR-01 | Tài khoản | Người sử dụng có một trong ba vai trò: Administrator, Operator hoặc Technician. Collector Agent sử dụng cơ chế xác thực riêng. |
| BR-02 | Tài khoản | Chỉ tài khoản đang hoạt động được đăng nhập và truy cập API được bảo vệ. |
| BR-03 | Tài khoản | Email phải được chuẩn hóa và duy nhất trong hệ thống. |
| BR-04 | Phân quyền | Backend phải kiểm tra quyền cho từng thao tác. Chỉ Administrator được quản trị tài khoản; ẩn menu không thay thế kiểm tra quyền tại API. |
| BR-05 | Bảo mật | Mật khẩu được lưu dưới dạng hash. API và nhật ký không được tiết lộ mật khẩu, password hash, JWT hoặc thông tin xác thực Agent. |
| BR-06 | Tài sản | Tài sản được tổ chức theo cấu trúc Site → Room → Rack → Node → Workload. Mỗi tài sản con thuộc một tài sản cha tương ứng. |
| BR-07 | Tài sản | Tài sản cha phải tồn tại khi tạo hoặc chuyển tài sản. Nếu cập nhật bị từ chối, quan hệ cũ phải được giữ nguyên. |
| BR-08 | Tài sản | Mã Site và Node duy nhất toàn hệ thống; mã Room duy nhất trong Site; mã Rack duy nhất trong Room; mã Workload duy nhất trong Node. |
| BR-09 | Tài sản | Serial Number của Node phải duy nhất khi có giá trị. Runtime ID của Workload phải duy nhất trong cùng Node khi có giá trị. |
| BR-10 | Tài sản | Capacity U của Rack là số nguyên từ 1 đến 100 theo thiết kế hiện tại. Kiểm tra vị trí lắp đặt và số U sử dụng chỉ áp dụng khi có chức năng tương ứng. |
| BR-11 | Phân quyền | Administrator và Operator được tạo, cập nhật Site, Room, Rack và Node; chỉ Administrator được xóa; Technician được tra cứu. Quyền quản lý Workload được xác định khi triển khai. |
| BR-12 | Tài sản | Không xóa tài sản còn dữ liệu phụ thuộc bị ràng buộc. Không tự động xóa dây chuyền khi chưa có quy tắc được phê duyệt. |
| BR-13 | Telemetry | Telemetry phải liên kết với nguồn gửi hợp lệ và tài sản đã đăng ký. Agent chỉ gửi dữ liệu trong phạm vi được cấp quyền. |
| BR-14 | Telemetry | Dữ liệu phải có thời điểm ghi nhận. Dữ liệu đến muộn được xử lý theo chính sách tiếp nhận, không mặc định coi là dữ liệu hiện tại. |
| BR-15 | Giám sát | Chu kỳ thu thập, gửi dữ liệu, heartbeat và timeout được cấu hình riêng theo NFR. Không kết luận mất kết nối khi chưa đến chu kỳ gửi tiếp theo. |
| BR-16 | Telemetry | Giao diện phải thể hiện thời điểm cập nhật cuối và trạng thái dữ liệu. Không coi dữ liệu thiếu là giá trị bằng không hoặc dữ liệu cũ là dữ liệu mới. |
| BR-17 | Telemetry | Retry tuân theo chính sách đã thống nhất. Backend kiểm tra dữ liệu sai định dạng và xử lý mẫu trùng để tránh ghi lặp ngoài chính sách. |
| BR-18 | Cảnh báo | Cảnh báo được tạo hoặc cập nhật theo điều kiện đã cấu hình, có xét tính hợp lệ và độ mới của dữ liệu. |
| BR-19 | Cảnh báo | Áp dụng quy tắc chống trùng trước khi tạo cảnh báo. Việc tái kích hoạt và kết thúc tuân theo vòng đời cảnh báo. |
| BR-20 | Cảnh báo | Cảnh báo và ticket là hai đối tượng khác nhau. Tạo ticket từ cảnh báo theo cơ chế đã thống nhất; đóng ticket không tự kết thúc cảnh báo còn hiệu lực. |
| BR-21 | Ticket | Operator phân công ticket cho Technician phù hợp và đang hoạt động. Ticket phải có tài sản liên quan và thông tin bắt buộc theo thiết kế. |
| BR-22 | Ticket | Technician chỉ được cập nhật ticket được giao hoặc được cấp quyền. Backend phải kiểm tra phạm vi dữ liệu. |
| BR-23 | Ticket | Chuyển trạng thái phải tuân theo vòng đời ticket, vai trò và điều kiện chuyển trạng thái. |
| BR-24 | Ticket | Technician gửi kết quả xử lý; Operator kiểm tra và phê duyệt đóng ticket khi đủ điều kiện. Technician không tự phê duyệt đóng. |
| BR-25 | Bảo trì | Lịch sử cập nhật ghi nhận người thực hiện và thời điểm; kết quả bảo trì truy vết được về ticket và tài sản liên quan. |
| BR-26 | Mobile AR | Marker phải ánh xạ rõ ràng đến một tài sản tại thời điểm tra cứu. Marker không hợp lệ không được dẫn đến tài sản khác. |
| BR-27 | Mobile AR | Nhận diện được marker không đồng nghĩa có quyền xem dữ liệu. Backend vẫn phải kiểm tra quyền truy cập. |
| BR-28 | Audit | Sự kiện thuộc phạm vi audit phải ghi nhận người hoặc nguồn thực hiện, hành động, đối tượng, thời điểm và kết quả. |
| BR-29 | Audit | Chỉ người có quyền được tra cứu audit log. Không cho sửa hoặc xóa tùy ý qua giao diện nghiệp vụ; lưu giữ và xóa theo chính sách riêng. |
| BR-30 | Cấu hình | Cấu hình phải hợp lệ trước khi lưu và áp dụng. Phân biệt cấu hình đã lưu với cấu hình Agent đã nhận hoặc áp dụng. |

## Ghi chú

- Giới hạn Rack 1–100 U là ràng buộc thiết kế của dự án.
- Các quy tắc phải thống nhất với FR, NFR, Use Case, ERD,
  ma trận phân quyền và ca kiểm thử.
- Khi thay đổi quy tắc, cần cập nhật các thành phần liên quan.
