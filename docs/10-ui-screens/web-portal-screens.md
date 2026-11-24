# Mô tả màn hình Web Portal AR-IMMS

## 1. Mục đích

Mô tả các màn hình và điều hướng đã xây dựng
trong task khởi tạo Frontend, layout và điều hướng.

Các trang nghiệp vụ hiện là trang khung.
Tài liệu không mặc định chức năng CRUD, telemetry,
cảnh báo hoặc ticket đã được tích hợp.

## 2. Danh sách màn hình

| Mã | Màn hình | Đường dẫn | Người sử dụng |
|---|---|---|---|
| SCR-01 | Đăng nhập | / | Người chưa đăng nhập |
| SCR-02 | Dashboard | /dashboard | Administrator, Operator, Technician |
| SCR-03 | Tài sản | /assets | Administrator, Operator, Technician |
| SCR-04 | Quản lý tài khoản | /users | Administrator |
| SCR-05 | Không có quyền | /forbidden | Người đã đăng nhập |
| SCR-06 | Không tìm thấy trang | Đường dẫn không tồn tại | Mọi người sử dụng |

## 3. Layout dùng chung

Layout Portal gồm ba vùng:

| Thành phần | Nội dung |
|---|---|
| Sidebar | Tên hệ thống và menu điều hướng |
| Header | Email, vai trò và nút Đăng xuất |
| Vùng nội dung | Nội dung của trang đang mở |

### Quy tắc hiển thị

- Dashboard và Tài sản hiển thị cho cả ba vai trò.
- Quản lý tài khoản chỉ hiển thị cho Administrator.
- Menu đang chọn được đánh dấu theo đường dẫn.
- Thông tin tài khoản được xác minh qua Backend.
- Layout phải hiển thị phù hợp trên màn hình máy tính phổ biến.
- Trang đăng nhập và trang 404 sử dụng bố cục riêng.

## 4. SCR-01 — Đăng nhập

### Mục đích

Xác thực tài khoản trước khi truy cập Web Portal.

### Thành phần

| Thành phần | Mô tả |
|---|---|
| Email | Nhập địa chỉ email tài khoản |
| Mật khẩu | Nhập mật khẩu, mặc định được che |
| Hiện/ẩn mật khẩu | Chuyển cách hiển thị mật khẩu |
| Nút đăng nhập | Gửi yêu cầu xác thực |
| Thông báo lỗi | Hiển thị lỗi dữ liệu, xác thực hoặc kết nối |

### Hành vi

1. Người sử dụng nhập email và mật khẩu.
2. Ứng dụng gửi POST /auth/login.
3. Khi thành công, lưu thông tin phiên và chuyển đến /dashboard.
4. Portal xác minh tài khoản qua GET /auth/me.

### Trạng thái

- Chưa nhập đủ dữ liệu: yêu cầu bổ sung.
- Đang gửi: vô hiệu hóa nút gửi để hạn chế yêu cầu lặp.
- Sai thông tin: hiển thị lỗi xác thực.
- Không kết nối được Backend: hiển thị lỗi kết nối.

## 5. SCR-02 — Dashboard

### Mục đích

Cung cấp trang vào chính sau khi đăng nhập.

### Thành phần hiện có

- Header và Sidebar dùng chung.
- Tiêu đề Dashboard.
- Nội dung chào mừng.
- Thông báo khu vực tích hợp dữ liệu tổng quan.

### Phạm vi

Chưa có số liệu thống kê hoặc biểu đồ telemetry.
Các nội dung này được bổ sung theo task chức năng tương ứng.

## 6. SCR-03 — Tài sản

### Mục đích

Cung cấp điểm truy cập chức năng quản lý hạ tầng.

### Thành phần hiện có

- Header và Sidebar dùng chung.
- Tiêu đề Quản lý tài sản.
- Giới thiệu cấu trúc Site, Room, Rack, Server và Workload.

### Phạm vi

Trang hiện là khung điều hướng.
Chưa tích hợp danh sách, tìm kiếm hoặc form CRUD.

Các nút nghiệp vụ khi triển khai phải tuân theo ma trận phân quyền.

## 7. SCR-04 — Quản lý tài khoản

### Mục đích

Cung cấp khu vực quản trị tài khoản cho Administrator.

### Thành phần hiện có

- Header và Sidebar dùng chung.
- Tiêu đề Quản lý tài khoản.
- Nội dung giới thiệu phạm vi quản trị.

### Quyền truy cập

- Administrator được truy cập.
- Operator và Technician không thấy menu.
- Operator và Technician nhập trực tiếp /users
  được chuyển đến /forbidden.

### Phạm vi

Chưa tích hợp bảng tài khoản, tạo tài khoản hoặc đổi vai trò
trên giao diện.

Các API quản trị tài khoản vẫn phải được Backend bảo vệ.

## 8. SCR-05 — Không có quyền

### Mục đích

Thông báo người sử dụng không được phép truy cập trang.

### Thành phần

- Số 403.
- Tiêu đề Không có quyền truy cập.
- Thông báo giải thích.
- Nút Về Dashboard.

### Hành vi

Nút Về Dashboard chuyển đến /dashboard.

Số 403 là nội dung thông báo trên giao diện.
Mã HTTP của trang không được suy ra chỉ từ nội dung hiển thị.

## 9. SCR-06 — Không tìm thấy trang

### Mục đích

Thông báo đường dẫn không tồn tại.

### Thành phần

- Số 404.
- Tiêu đề Không tìm thấy trang.
- Thông báo giải thích.
- Nút Về Dashboard.
- Nút Về trang đăng nhập.

### Hành vi

- Về Dashboard: chuyển đến /dashboard,
  sau đó áp dụng kiểm tra phiên của Portal.
- Về trang đăng nhập: chuyển đến /.

## 10. Luồng điều hướng

- Đăng nhập thành công → Dashboard.
- Dashboard ↔ Tài sản.
- Administrator: Dashboard hoặc Tài sản → Quản lý tài khoản.
- Người thiếu quyền truy cập /users → Không có quyền.
- Không có quyền → Dashboard.
- Đăng xuất → Đăng nhập.
- Chưa đăng nhập truy cập trang được bảo vệ → Đăng nhập.
- Đường dẫn không tồn tại → Trang 404.

## 11. Xử lý phiên và lỗi kết nối

- Portal hiển thị trạng thái đang xác minh phiên.
- Không có phiên hợp lệ: chuyển về đăng nhập.
- Không xác minh được do lỗi kết nối:
  hiển thị lỗi cùng lựa chọn Thử lại hoặc Về trang đăng nhập.
- Không hiển thị nội dung Portal trước khi xác minh thành công.
- Đăng xuất xóa thông tin phiên tại trình duyệt.

## 12. Tiêu chí kiểm tra

| Nội dung | Kết quả mong đợi |
|---|---|
| Thông tin Header | Đúng email và vai trò |
| Điều hướng | Chuyển đúng trang, giữ layout chung |
| Menu đang chọn | Được đánh dấu rõ |
| Menu quản trị | Chỉ Administrator nhìn thấy |
| Truy cập /users trái quyền | Chuyển sang /forbidden |
| Đăng xuất | Trở về đăng nhập |
| Trang được bảo vệ khi chưa đăng nhập | Không hiển thị nội dung Portal |
| URL không tồn tại | Hiển thị trang 404 |
| Màn hình 1366×768 và 1920×1080 | Nội dung không chồng lấn hoặc tràn ngang |

## 13. Ngôn ngữ và ảnh minh họa

Bản giao diện đã kiểm tra sử dụng tiếng Việt ở phần Portal
và còn nội dung tiếng Anh tại trang đăng nhập.

NFR hiện yêu cầu Web sử dụng tiếng Anh.
Nhóm cần thống nhất và cập nhật giao diện hoặc yêu cầu
trước khi nghiệm thu.

Ảnh minh họa phải lấy từ giao diện thực tế,
không chứa mật khẩu, JWT hoặc thông tin bí mật.

## 14. Tài liệu liên quan

- [Frontend README](../../frontend/README.md)
- [Ma trận phân quyền](../01-users-and-rbac/role-permissions.md)
- [Báo cáo Sprint 3](../08-sprints/sprint-3.md)