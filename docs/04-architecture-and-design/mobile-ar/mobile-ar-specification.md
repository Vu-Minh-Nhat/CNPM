# Task 57 — Đặc tả Mobile AR

## 1. Mục đích

Tài liệu này chốt phạm vi sử dụng Mobile AR tại hiện trường, nền tảng kiểm thử, loại Marker, nội dung hiển thị, phân quyền và các hành vi lỗi phục vụ nghiệm thu cuối dự án AR-IMMS.

## 2. Đối tượng sử dụng

Mobile AR phục vụ **Technician** trong quá trình kiểm tra thiết bị và xử lý công việc bảo trì tại hiện trường.

Các chức năng chính:

- Quét Marker của thiết bị.
- Nhận diện và ánh xạ Marker với Node.
- Tra cứu thông tin thiết bị.
- Xem thông tin telemetry và trạng thái kết nối theo phạm vi dữ liệu hệ thống cung cấp.
- Xem công việc/Ticket được giao.
- Cập nhật kết quả xử lý Ticket theo quyền được cấp.

## 3. Nền tảng và thiết bị kiểm thử

### Nền tảng

- **Mobile:** React Native.
- **Nền tảng kiểm thử mục tiêu:** Android.
- **Backend:** API của AR-IMMS.
- **Authentication:** JWT.
- **Authorization:** RBAC.

### Thiết bị kiểm thử

Thiết bị cụ thể phải được nhóm ghi nhận trước khi nghiệm thu:

| STT | Thiết bị | Android | Camera | Kết quả |
|---|---|---|---|---|
| 1 | Thiết bị Android kiểm thử chính | Ghi phiên bản thực tế | Có | Pending |
| 2 | Thiết bị Android kiểm thử phụ | Ghi phiên bản thực tế | Có | Pending |

> **Lưu ý:** Không sử dụng danh sách thiết bị này để tuyên bố hỗ trợ toàn bộ thiết bị Android.

## 4. Marker

Phạm vi sản phẩm đã mô tả nhận diện thiết bị thông qua:

- QR
- ArUco

Task 57 chốt việc nghiệm thu theo Marker thực tế mà nhóm đã triển khai và có thể cung cấp bằng chứng.

Nếu bản Mobile hiện tại chỉ triển khai một loại Marker thì chỉ đưa loại đó vào tiêu chí `PASS`; loại còn lại phải ghi là:

- Ngoài phạm vi triển khai hiện tại; hoặc
- Chưa có bằng chứng.

> **Lưu ý:** Không đánh dấu `PASS` nếu chưa có chức năng thực tế và bằng chứng kiểm thử.

## 5. Luồng Mobile AR

```text
Technician
  |
  v
Đăng nhập Mobile
  |
  v
Kiểm tra JWT + quyền Technician
  |
  v
Mở chức năng AR Scanner
  |
  v
Xin quyền Camera
  +---- Từ chối ----> Thông báo yêu cầu quyền Camera
  |
  v
Quét Marker
  +---- Không hợp lệ ----> Thông báo Marker không hợp lệ
  |
  v
Nhận diện Marker
  |
  v
Ánh xạ Marker -> Node
  |
  v
Hiển thị thông tin Node
  +---- Có dữ liệu telemetry ----> Hiển thị telemetry
  +---- Có trạng thái kết nối ---> Hiển thị trạng thái
  +---- Có cảnh báo ------------> Hiển thị cảnh báo
  |
  v
Xem Ticket liên quan
  |
  v
Technician cập nhật kết quả xử lý
  |
  v
Backend lưu thay đổi
```

---

## 6. Danh sách màn hình

Luồng Mobile AR tối thiểu gồm các màn hình/chức năng sau:

| STT | Màn hình / chức năng | Người dùng | Mục đích |
|---|---|---|---|
| 1 | Login | Technician | Xác thực tài khoản |
| 2 | AR Scanner | Technician | Quét Marker |
| 3 | Node Information | Technician | Hiển thị thông tin Node |
| 4 | Telemetry | Technician | Xem dữ liệu telemetry |
| 5 | Connection Status | Technician | Xem trạng thái kết nối |
| 6 | Alert | Technician | Xem cảnh báo liên quan |
| 7 | Ticket | Technician | Xem Ticket được giao |
| 8 | Ticket Update | Technician | Cập nhật kết quả xử lý |
| 9 | Error / Permission | Technician | Hiển thị lỗi và trạng thái không hợp lệ |

> **Lưu ý:** Tên màn hình thực tế có thể khác tên trong bảng nhưng phải đáp ứng cùng mục đích nghiệp vụ.

## 7. Nội dung hiển thị sau khi nhận diện Node

Sau khi Marker được ánh xạ thành công với Node, Mobile có thể hiển thị các thông tin thuộc phạm vi dữ liệu hệ thống cung cấp.

### Thông tin định danh

- Node ID.
- Node code hoặc tên định danh.
- Thông tin nhận diện thiết bị phù hợp với dữ liệu Backend.

### Vị trí

- Site.
- Room.
- Rack.
- Vị trí khác nếu Backend có cung cấp.

### Telemetry

- Các chỉ số telemetry được Backend cung cấp.
- Thời điểm cập nhật dữ liệu nếu có.

### Trạng thái kết nối

- Trạng thái kết nối của Node theo dữ liệu hệ thống.

### Cảnh báo

- Alert liên quan đến Node nếu có.
- Trạng thái hoặc mức độ cảnh báo nếu Backend cung cấp.

> **Bảo mật:** Không hiển thị password, password hash, JWT secret hoặc thông tin bảo mật nội bộ.

## 8. Phân quyền

Mobile AR áp dụng RBAC của hệ thống.

### Technician

Được phép:

- Đăng nhập Mobile.
- Sử dụng chức năng AR Scanner.
- Tra cứu Node.
- Xem telemetry và trạng thái liên quan.
- Xem Ticket được phân công.
- Cập nhật kết quả Ticket theo quyền được cấp.

### Operator

- Không thuộc phạm vi sử dụng Mobile AR dành cho Technician nếu không được Backend cấp quyền tương ứng.

### Administrator

- Có quyền quản trị theo RBAC của hệ thống nhưng không mặc định thay thế luồng nghiệp vụ Technician trên Mobile.

> **Lưu ý:** Backend phải kiểm tra quyền thực tế; không chỉ dựa vào việc ẩn/hiện chức năng trên giao diện Mobile.

## 9. Thao tác Ticket của Technician

Luồng Ticket của Technician:

```text
Technician đăng nhập
  |
  v
Xem Ticket được giao
  |
  v
Chọn Ticket
  |
  v
Xem thông tin công việc
  |
  v
Thực hiện xử lý tại hiện trường
  |
  v
Cập nhật kết quả xử lý
  |
  v
Gửi thay đổi lên Backend
  |
  v
Backend kiểm tra JWT + quyền
  |
  v
Lưu kết quả
```

## 10. Xử lý lỗi

### 10.1 Camera bị từ chối

Khi Technician từ chối quyền Camera:

- Không tiếp tục quét Marker.
- Hiển thị thông báo yêu cầu quyền Camera.
- Cho phép người dùng quay lại hoặc cấp quyền Camera theo cơ chế của Android.

### 10.2 Marker không hợp lệ

Khi Marker không nhận diện được hoặc không ánh xạ được với Node:

- Không hiển thị dữ liệu Node không xác định.
- Thông báo Marker không hợp lệ hoặc không tìm thấy thiết bị.
- Cho phép Technician thực hiện lại thao tác quét.

### 10.3 Mất mạng

Khi Mobile mất kết nối Backend:

- Hiển thị trạng thái lỗi kết nối.
- Không giả lập dữ liệu mới.
- Các thao tác cần Backend phải được thông báo không thể thực hiện nếu chưa có cơ chế offline được triển khai.
- Khi có mạng trở lại, Technician có thể thực hiện lại thao tác.

### 10.4 Phiên JWT hết hạn

Khi JWT hết hạn hoặc không còn hợp lệ:

- Backend từ chối request theo cơ chế authentication.
- Mobile phải thông báo phiên đăng nhập không còn hợp lệ.
- Technician thực hiện đăng nhập lại.
- Không tiếp tục sử dụng dữ liệu hoặc quyền từ phiên đã hết hạn.

### 10.5 Không đủ quyền

Khi Technician gọi chức năng/API không thuộc quyền:

- Backend từ chối request.
- Mobile hiển thị thông báo không đủ quyền.
- Không thực hiện thao tác bị hạn chế.

## 11. Dữ liệu và trạng thái

Mobile AR sử dụng dữ liệu từ Backend/API của AR-IMMS.

Các dữ liệu chính gồm:

| Dữ liệu | Nguồn | Mục đích |
|---|---|---|
| User | Authentication API | Xác định Technician |
| JWT | Authentication API | Xác thực request |
| Node | Node/Asset API | Nhận diện thiết bị |
| Marker mapping | Dữ liệu hệ thống | Ánh xạ Marker → Node |
| Telemetry | Telemetry API | Hiển thị thông số |
| Connection status | Backend | Hiển thị trạng thái |
| Alert | Alert API | Hiển thị cảnh báo |
| Ticket | Ticket API | Xử lý công việc |

> **Lưu ý:** Mobile không tự quyết định quyền truy cập bằng dữ liệu giao diện. Quyền phải được kiểm tra ở Backend.

## 12. Phạm vi bắt buộc nghiệm thu

Các nội dung sau là phạm vi bắt buộc phải được nhóm xác nhận trước nghiệm thu:

- Có luồng đăng nhập Mobile.
- Có kiểm tra JWT.
- Có kiểm tra quyền Technician.
- Có chức năng AR Scanner nếu thuộc phạm vi triển khai.
- Có Marker thực tế được nhóm cam kết hỗ trợ.
- Có ánh xạ Marker với Node.
- Có hiển thị thông tin Node theo dữ liệu Backend.
- Có xử lý Camera permission.
- Có xử lý Marker không hợp lệ.
- Có xử lý mất mạng.
- Có xử lý JWT hết hạn.
- Có xử lý không đủ quyền.
- Có luồng Ticket dành cho Technician nếu thuộc phạm vi đề tài.
- Có bằng chứng kiểm thử tương ứng.

> **Lưu ý:** Chỉ đánh dấu `PASS` khi có cả chức năng thực tế và bằng chứng.

## 13. Ngoài phạm vi

Các nội dung sau không được tự động xem là tiêu chí `PASS` nếu chưa có triển khai và bằng chứng:

- Hỗ trợ toàn bộ thiết bị Android.
- Hỗ trợ tất cả phiên bản Android.
- Hỗ trợ đồng thời QR và ArUco nếu bản Mobile thực tế chưa triển khai cả hai.
- Chế độ offline đầy đủ nếu chưa được triển khai.
- Tự động đồng bộ dữ liệu offline nếu chưa có cơ chế thực tế.
- Các chức năng quản trị tài khoản trên Mobile.
- Hiển thị thông tin bảo mật như password hash hoặc JWT secret.
- Các chức năng không nằm trong phạm vi đề tài hoặc chưa được nhóm cam kết.

## 14. Tiêu chí PASS

Một chức năng Mobile AR được xem là `PASS` khi thỏa cả ba điều kiện:

1. Có yêu cầu hoặc phạm vi được thống nhất.
2. Có chức năng thực tế trong hệ thống.
3. Có test case và bằng chứng kiểm thử.

### Phân loại kết quả

| Trạng thái | Ý nghĩa |
|---|---|
| **PASS** | Đã triển khai và có bằng chứng |
| **FAIL** | Đã kiểm thử nhưng không đạt |
| **Pending** | Chưa có đủ bằng chứng hoặc chưa xác nhận triển khai |
| **Out of scope** | Không thuộc phạm vi triển khai |

> **Lưu ý:** Không dùng đặc tả tài liệu để thay thế bằng chứng của chức năng thực tế.