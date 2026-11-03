# Ma trận phân quyền hệ thống AR-IMMS

## 1. Mục đích

Quy định quyền truy cập theo vai trò nhằm thống nhất
việc xây dựng Backend, Web Portal, Mobile AR và kiểm thử.

Hệ thống có ba vai trò người sử dụng:

- Administrator: quản trị viên.
- Operator: nhân viên vận hành.
- Technician: kỹ thuật viên.

## 2. Quy ước

| Ký hiệu | Ý nghĩa |
|---|---|
| Có | Được phép thực hiện |
| Không | Không được phép thực hiện |
| Theo phạm vi | Chỉ được thực hiện trên dữ liệu hoặc công việc được cấp quyền |

Ma trận dưới đây phân biệt quyền của Backend lõi
và quyền nghiệp vụ dự kiến cho các chức năng phát triển tiếp.

## 3. Phân quyền Backend lõi

| Chức năng | Administrator | Operator | Technician |
|---|---|---|---|
| Xem thông tin tài khoản đang đăng nhập | Có | Có | Có |
| Truy cập Dashboard | Có | Có | Có |
| Xem danh sách và chi tiết Site | Có | Có | Có |
| Tạo và cập nhật Site | Có | Có | Không |
| Xóa Site | Có | Không | Không |
| Xem danh sách và chi tiết Room | Có | Có | Có |
| Tạo và cập nhật Room | Có | Có | Không |
| Xóa Room | Có | Không | Không |
| Xem danh sách và chi tiết Rack | Có | Có | Có |
| Tạo và cập nhật Rack | Có | Có | Không |
| Xóa Rack | Có | Không | Không |
| Xem danh sách và chi tiết Server | Có | Có | Có |
| Tạo và cập nhật Server | Có | Có | Không |
| Xóa Server | Có | Không | Không |
| Truy cập chức năng quản lý tài khoản | Có | Không | Không |

Được cấp quyền không có nghĩa thao tác luôn thành công.
Dữ liệu đầu vào và các ràng buộc nghiệp vụ vẫn phải được kiểm tra.

Ví dụ: Administrator không được xóa Site còn chứa Room.

## 4. Quyền trên Web Portal

| Trang | Đường dẫn | Vai trò được phép |
|---|---|---|
| Đăng nhập | / | Không yêu cầu đăng nhập |
| Dashboard | /dashboard | Administrator, Operator, Technician |
| Tài sản | /assets | Administrator, Operator, Technician |
| Quản lý tài khoản | /users | Administrator |
| Không có quyền | /forbidden | Người đã đăng nhập |

### 4.1. Hiển thị menu

- Cả ba vai trò nhìn thấy Dashboard và Tài sản.
- Chỉ Administrator nhìn thấy Quản lý tài khoản.
- Menu đang chọn phải được thể hiện rõ.
- Vai trò hiển thị được lấy từ thông tin tài khoản
  đã xác minh qua Backend.

### 4.2. Truy cập trực tiếp bằng URL

- Người chưa đăng nhập truy cập trang được bảo vệ
  được chuyển về trang đăng nhập.
- Operator hoặc Technician truy cập /users
  được chuyển đến /forbidden.
- Ẩn menu không thay thế kiểm tra quyền khi truy cập trực tiếp.

### 4.3. Phạm vi triển khai giao diện

Các trang Dashboard, Tài sản và Quản lý tài khoản
hiện cung cấp khung giao diện và điều hướng.

Quyền tại API không đồng nghĩa giao diện đã có đầy đủ
bảng dữ liệu hoặc các thao tác tạo, sửa và xóa.

## 5. Phân công quyền nghiệp vụ dự kiến

Phần này mô tả định hướng cho các chức năng phát triển tiếp.
Quyền chi tiết phải được xác định trong yêu cầu của từng chức năng.

| Nhóm chức năng | Vai trò phụ trách | Phạm vi |
|---|---|---|
| Quản lý tài khoản và gán vai trò | Administrator | Tài khoản thuộc hệ thống |
| Cấu hình và sức khỏe hệ thống | Administrator | Phạm vi quản trị được cấp |
| Tra cứu audit log | Administrator | Nhật ký thuộc phạm vi được cấp |
| Giám sát telemetry và cảnh báo | Operator | Tài sản thuộc phạm vi vận hành |
| Cấu hình điều kiện cảnh báo | Operator | Theo quyền cấu hình được cấp |
| Tạo và phân công ticket | Operator | Công việc thuộc phạm vi phụ trách |
| Phê duyệt đóng ticket | Operator | Sau khi kiểm tra kết quả xử lý |
| Xem ticket được giao | Technician | Theo phạm vi công việc được giao |
| Cập nhật tiến độ và kết quả bảo trì | Technician | Theo phạm vi công việc được giao |
| Quét marker và tra cứu thiết bị | Technician | Tài sản được phép truy cập |
| Xem telemetry phục vụ bảo trì | Technician | Theo phạm vi được cấp |

Không mặc định Administrator có mọi quyền nghiệp vụ.
Nếu Administrator cần thực hiện công việc vận hành hoặc bảo trì,
quyền đó phải được quy định rõ trong thiết kế.

## 6. Nguyên tắc kiểm tra quyền tại Backend

### 6.1. Xác thực

- Các API được bảo vệ yêu cầu JWT hợp lệ.
- Backend kiểm tra tài khoản còn tồn tại và đang hoạt động.
- Vai trò dùng để phân quyền phải phản ánh tài khoản hiện tại.
- Không tin cậy vai trò do Frontend tự gửi lên.

### 6.2. Phân quyền theo vai trò

- Backend kiểm tra vai trò trước khi thực hiện thao tác.
- API được bảo vệ phải khai báo quyền truy cập rõ ràng.
- API không có cấu hình quyền phù hợp phải bị từ chối,
  trừ khi được khai báo công khai có chủ đích.

### 6.3. Phân quyền theo dữ liệu

Vai trò không thay thế kiểm tra phạm vi dữ liệu.

Ví dụ: Technician được cập nhật kết quả bảo trì
nhưng chỉ trên ticket được giao hoặc được cấp quyền.

Quy tắc này được triển khai cùng chức năng ticket.

## 7. Phản hồi khi bị từ chối

| Trường hợp | Phản hồi tại API |
|---|---|
| Thiếu JWT, JWT không hợp lệ hoặc hết hạn | 401 Unauthorized |
| Tài khoản bị vô hiệu hóa khi truy cập API được bảo vệ | 401 Unauthorized |
| Đã xác thực nhưng không đủ quyền | 403 Forbidden |

Trang /forbidden là thông báo trên giao diện.
Hiển thị số 403 trên trang không tự bảo đảm
phản hồi HTTP của trang mang mã 403.

API phải trả mã trạng thái theo cơ chế xác thực và phân quyền.

## 8. Collector Agent

Collector Agent sử dụng cơ chế xác thực riêng theo thiết kế.

- Không dùng JWT của tài khoản người sử dụng để thay thế
  thông tin xác thực Agent.
- Chỉ được gửi dữ liệu cho tài sản hoặc nguồn dữ liệu được cấp.
- Không được truy cập API quản trị tài khoản.
- Thông tin xác thực Agent phải có khả năng thu hồi theo thiết kế.

Các quyền này là yêu cầu cho chức năng Agent,
không khẳng định đã được triển khai trong Backend lõi.

## 9. Tiêu chí kiểm thử

- Administrator thấy menu và truy cập được /users.
- Operator và Technician không thấy menu Quản lý tài khoản.
- Operator và Technician nhập /users được chuyển sang /forbidden.
- Người chưa đăng nhập không xem được nội dung Portal được bảo vệ.
- Đăng xuất xóa thông tin phiên tại trình duyệt.
- API được bảo vệ từ chối yêu cầu thiếu hoặc sai JWT bằng mã 401.
- Technician được xem tài sản nhưng bị từ chối tạo tài sản bằng mã 403.
- Operator bị từ chối xóa Site, Room, Rack và Server bằng mã 403.
- Administrator vẫn phải tuân thủ ràng buộc dữ liệu khi xóa tài sản.

Kết quả thực tế và bằng chứng kiểm thử được ghi
trong báo cáo kiểm thử tương ứng.

## 10. Tài liệu liên quan

- [Các tác nhân của hệ thống](01-system-actors.md)
- [Phạm vi và sơ đồ ngữ cảnh](../00-overview/04-scope-and-context.md)
- [Hướng dẫn Backend](../../backend/README.md)
- [Hướng dẫn Frontend](../../frontend/README.md)
