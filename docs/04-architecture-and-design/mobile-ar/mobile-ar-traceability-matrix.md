# Task 57 — Ma trận truy vết Mobile AR

## 1. Mục đích

Ma trận này truy vết từ yêu cầu Mobile AR đến chức năng, test case và bằng chứng nghiệm thu.

| ID | Yêu cầu | Chức năng | Test case | Bằng chứng | Trạng thái |
|---|---|---|---|---|---|
| FR-05-01 | Technician sử dụng Mobile AR tại hiện trường | Đăng nhập Mobile và mở AR Scanner | TC-MAR-01 | Screenshot màn hình Login và AR Scanner | Pending |
| FR-05-02 | Nhận diện Node bằng Marker | Quét QR/ArUco và ánh xạ Marker với Node | TC-MAR-02 | Video/screenshot quá trình scan và Node được nhận diện | Pending |
| FR-05-03 | Hiển thị thông tin Node | Hiển thị định danh, vị trí, telemetry | TC-MAR-03 | Screenshot màn hình Node Information | Pending |
| FR-05-04 | Hiển thị trạng thái kết nối | Hiển thị Online/Offline hoặc trạng thái kết nối tương ứng | TC-MAR-04 | Screenshot trạng thái kết nối | Pending |
| FR-05-05 | Hiển thị cảnh báo | Hiển thị Alert liên quan đến Node | TC-MAR-05 | Screenshot màn hình Alert | Pending |
| FR-05-06 | Technician thao tác Ticket | Xem và cập nhật Ticket trên Mobile | TC-MAR-06 | Screenshot Ticket trước và sau khi cập nhật | Pending |
| RBAC-01 | Technician được sử dụng luồng Mobile AR | Kiểm tra quyền Technician | TC-MAR-07 | Screenshot tài khoản Technician và kết quả truy cập | Pending |
| RBAC-02 | Người không có quyền không được thực hiện chức năng | Backend kiểm tra quyền theo JWT/RBAC | TC-MAR-08 | Screenshot/API response khi không đủ quyền | Pending |
| ERR-01 | Camera bị từ chối | Hiển thị thông báo quyền camera | TC-MAR-09 | Screenshot thông báo lỗi | Pending |
| ERR-02 | Marker không hợp lệ | Từ chối Marker không hợp lệ và thông báo lỗi | TC-MAR-10 | Screenshot thông báo Marker không hợp lệ | Pending |
| ERR-03 | Mất mạng | Hiển thị trạng thái lỗi mạng và không làm sai lệch dữ liệu | TC-MAR-11 | Screenshot/video khi ngắt mạng | Pending |
| ERR-04 | JWT hết hạn | Yêu cầu đăng nhập lại khi phiên hết hạn | TC-MAR-12 | Screenshot màn hình yêu cầu đăng nhập lại | Pending |
| DATA-01 | Dữ liệu Mobile lấy từ hệ thống | Mobile sử dụng dữ liệu Node/Telemetry/Alert/Ticket từ backend | TC-MAR-13 | Screenshot Mobile đối chiếu dữ liệu backend | Pending |

## 2. Quy ước trạng thái

| Trạng thái | Ý nghĩa |
|---|---|
| PASS | Đã kiểm thử và có bằng chứng đạt yêu cầu |
| FAIL | Đã kiểm thử nhưng chưa đạt yêu cầu |
| Pending | Chưa thực hiện kiểm thử hoặc chưa có bằng chứng |
| Out of scope | Không thuộc phạm vi nghiệm thu của Task 57 |

## 3. Quy tắc nghiệm thu

Một yêu cầu chỉ được đánh dấu `PASS` khi:

1. Chức năng đã được triển khai hoặc có cơ sở xác nhận từ hệ thống hiện tại.
2. Test case tương ứng đã được thực hiện.
3. Có bằng chứng nghiệm thu phù hợp.
4. Kết quả thực tế phù hợp với yêu cầu.

Không đánh dấu `PASS` chỉ dựa trên việc chức năng được mô tả trong tài liệu.