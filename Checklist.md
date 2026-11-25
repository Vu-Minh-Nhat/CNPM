# Checklist tổng dự án AR-IMMS

Checklist phản ánh tình trạng triển khai thực tế.
Task, người phụ trách, thời hạn và review được quản lý trên Jira.

- `[x]`: đã triển khai và có kiểm tra/bằng chứng.
- `[ ]`: chưa hoàn thành hoặc chưa có bằng chứng nghiệm thu.
- Không đánh dấu hoàn thành chỉ vì có tài liệu hoặc code chưa chạy.

---

## 1. Phân tích, yêu cầu và thiết kế

### Tổng quan và phạm vi

- [x] Mô tả bối cảnh AR-IMMS và Mini Data Center Testbed.
- [x] Xác định mục tiêu dự án.
- [x] Xác định phạm vi Web Portal, Backend, Collector Agent và Mobile AR.
- [x] Nêu giới hạn và phần ngoài phạm vi.
- [x] Xác định các vai trò Administrator, Operator, Technician và Collector Agent.
- [x] Hoàn thiện sơ đồ ngữ cảnh, Use Case và ERD.
- [x] Lập danh sách yêu cầu chức năng FR-01 đến FR-15.
- [x] Lập danh sách yêu cầu phi chức năng NFR-01 đến NFR-19.
- [x] Lập quy tắc nghiệp vụ và ma trận phân quyền.

### Tài liệu

- [x] Tài liệu Markdown được tổ chức trong `docs/`.
- [x] Có README gốc và README cho Backend/Frontend.
- [x] Có tài liệu kiến trúc, ERD, API và kiểm thử.
- [X] Cập nhật toàn bộ tài liệu để phản ánh đầy đủ Alert, Ticket, Marker và Mobile AR sau khi triển khai.
- [X] Rà soát liên kết tài liệu không còn trỏ đến NestJS hoặc cấu trúc cũ.

---

## 2. Nền tảng Backend Flask

### Hạ tầng và Database

- [x] Backend sử dụng Python Flask.
- [x] Sử dụng PostgreSQL, SQLAlchemy và Alembic.
- [x] Có endpoint kiểm tra sức khỏe `/health`.
- [x] Cấu hình Backend bằng biến môi trường.
- [x] Có migration khởi tạo tài khoản, vai trò và cây tài sản.
- [x] Có seed dữ liệu mẫu: tài khoản, Site, Room, Rack, Node và Workload.
- [x] Seed chạy lại không tạo dữ liệu trùng.
- [x] Có migration lưu telemetry.
- [x] Có migration lưu Alert, Ticket và Marker.
- [ ] Sửa migration `9826d73dbfbd` để không thêm trùng cột `last_telemetry_received_at`.
- [ ] Kiểm tra migration từ database trống trên bản `main` sau khi sửa lỗi.
- [ ] Kiểm tra migration và seed từ bản clone sạch.

### Đăng nhập và phân quyền

- [x] Đăng nhập bằng email và mật khẩu.
- [x] Mật khẩu được hash bằng bcrypt.
- [x] Cấp JWT khi đăng nhập thành công.
- [x] API `/auth/me` trả thông tin người dùng hiện tại.
- [x] Backend kiểm tra xác thực và RBAC.
- [x] Xử lý lỗi 401 và 403.
- [x] Administrator quản lý tài khoản.
- [x] Operator và Technician bị từ chối API quản lý tài khoản.
- [x] Có Swagger/OpenAPI cơ bản.
- [x] Kiểm tra lại toàn bộ API sau khi thêm Alert, Ticket và Marker.

### Cây tài sản

- [x] CRUD Site.
- [x] CRUD Room.
- [x] CRUD Rack.
- [x] CRUD Node/Server.
- [x] Tra cứu Node cùng Site → Room → Rack → Workload.
- [x] Kiểm tra khóa ngoại, mã trùng và ràng buộc dữ liệu.
- [x] Áp dụng quyền Administrator, Operator và Technician.
- [ ] Kiểm thử hồi quy cây tài sản sau mỗi migration Sprint 5 và Sprint 6.

---

## 3. Web Management Portal

### Nền tảng giao diện

- [x] Khởi tạo Next.js và TypeScript.
- [x] Cấu hình địa chỉ Backend qua `NEXT_PUBLIC_API_URL`.
- [x] Có `.env.example`.
- [x] Có Header, Sidebar và Portal Layout.
- [x] Hiển thị menu theo vai trò.
- [x] Có trang không đủ quyền truy cập.
- [x] Có trang đăng nhập, đăng xuất và xử lý phiên hết hạn.
- [x] Gọi API với JWT.
- [x] Xử lý tải, rỗng, lỗi API và lỗi mạng ở các màn hình đã triển khai.

### Tài sản và tài khoản

- [x] Danh sách tài sản từ API.
- [x] Tìm kiếm và lọc tài sản theo Site.
- [x] Xem chi tiết Node, Rack, Room, Site và Workload.
- [x] Administrator xem danh sách tài khoản.
- [x] Administrator tạo tài khoản.
- [x] Administrator thay đổi vai trò.
- [x] Kiểm tra giao diện bị hạn chế theo vai trò.
- [x] Hoàn thiện Dashboard từ dữ liệu tài sản và giám sát thật.
- [x] Kiểm thử đầy đủ giao diện dưới cả ba vai trò.

### Telemetry trên Web

- [x] Hiển thị CPU, RAM và Disk của Node.
- [x] Hiển thị thời điểm đo và thời điểm Backend nhận dữ liệu.
- [x] Phân biệt Node chưa từng gửi dữ liệu.
- [x] Phân biệt dữ liệu mới và dữ liệu cũ.
- [x] Phân biệt trạng thái đang kết nối và mất kết nối.
- [x] Tự cập nhật telemetry theo chu kỳ.
- [x] Có biểu đồ lịch sử CPU, RAM và Disk.
- [x] Có lựa chọn khoảng lịch sử 5, 15 và 60 phút.
- [x] Hủy request/timer khi đổi Node hoặc rời trang.
- [x] Lint và build Frontend đã đạt.
- [ ] Lưu ảnh/video kiểm thử dữ liệu mới, dữ liệu cũ, mất kết nối và kết nối lại.

---

## 4. Collector Agent và Telemetry

### Collector Agent

- [x] Thu thập CPU, RAM và Disk từ máy chạy Agent.
- [x] Tạo `message_id`, `node_id` và `measured_at`.
- [x] Gửi telemetry theo chu kỳ mặc định 5 giây.
- [x] Có timeout, retry và log lỗi gửi dữ liệu.
- [x] Có `agent/run.bat` để chạy nhanh.
- [x] Agent dùng `X-Agent-Key` khớp Backend.
- [x] Hoàn thiện `agent/.env.example` không chứa JWT, token hoặc khóa thực.
- [X] Kiểm tra Agent từ bản clone sạch.
- [ ] Kiểm tra retry khi Backend hoặc mạng gián đoạn.

### Lưu trữ và API Telemetry

- [x] Telemetry liên kết với Node hợp lệ.
- [x] Kiểm tra timestamp có timezone.
- [x] Kiểm tra CPU, RAM và Disk trong khoảng 0–100.
- [x] Ngăn telemetry trùng bằng `message_id` và Node.
- [x] Có truy vấn mẫu mới nhất.
- [x] Có truy vấn lịch sử theo khoảng thời gian.
- [x] Lưu thời điểm liên lạc hợp lệ gần nhất của Node.
- [x] Phát hiện dữ liệu cũ sau 30 giây.
- [x] Phát hiện mất kết nối sau 90 giây.
- [x] Có kiểm thử repository và logic trạng thái.
- [ ] Thay API key bằng mTLS nếu nhóm giữ NFR-07 là yêu cầu bắt buộc nghiệm thu.

---

## 5. Sprint 5 — Cảnh báo và Ticket bảo trì

### Lưu trữ Alert, Alert Rule và Ticket

- [x] Có model Alert Rule.
- [x] Có model Alert.
- [x] Có model Ticket và Ticket History.
- [x] Có migration lưu Alert, Ticket và quan hệ liên quan.
- [x] Có repository Alert, Ticket và Ticket History.
- [x] Kiểm thử migration Alert/Ticket từ database trống.
- [x] Kiểm thử khóa ngoại, trạng thái, chống trùng và cập nhật đồng thời.

### Phát hiện và quản lý cảnh báo

- [x] Tạo, xem, cập nhật, bật/tắt Alert Rule.
- [x] Cấu hình ngưỡng CPU, RAM và Disk.
- [x] Cấu hình cảnh báo mất kết nối.
- [x] Kiểm tra dữ liệu cũ không được dùng như dữ liệu hiện tại.
- [x] Tự tạo Alert khi telemetry vượt ngưỡng.
- [ ] Tự tạo Alert khi Node mất kết nối quá ngưỡng.
- [ ] Chống Alert trùng cho cùng Node và Rule đang hoạt động.
- [ ] Xử lý phục hồi Alert khi điều kiện kết thúc.
- [ ] Phân biệt Alert đang hoạt động, đã xác nhận và đã phục hồi.
- [x] Có tiến trình kiểm tra mất kết nối khi Agent không gửi dữ liệu.
- [x] Có API danh sách, chi tiết, bộ lọc và phân trang Alert.
- [x] Có API xác nhận Alert theo quyền.
- [ ] Cập nhật Swagger/OpenAPI.
- [ ] Kiểm thử API, quyền và vòng đời Alert.

### Giao diện cảnh báo — Task 6

- [x] Có trang `/alerts`.
- [x] Hiển thị Node, mức độ, nguyên nhân, giá trị, ngưỡng và thời điểm.
- [x] Có bộ lọc theo Node, mức độ, trạng thái và thời gian.
- [x] Có phân trang.
- [x] Có trang/khung chi tiết Alert.
- [x] Có thao tác xác nhận Alert theo quyền.
- [x] Có giao diện tạo, sửa, bật/tắt Alert Rule.
- [x] Không hiển thị thao tác vượt quyền.
- [x] Có thao tác tạo Ticket từ Alert và điền sẵn Alert/Node.
- [x] Có xử lý tải, rỗng, lỗi API, 401 và 403.
- [ ] Dọn timer/request khi rời trang.
- [ ] Lint và build đạt.
- [ ] Có ảnh/video kiểm thử trên Jira.

### Ticket và bảo trì

- [x] Tạo Ticket thủ công.
- [x] Tạo Ticket từ Alert.
- [x] Liên kết Ticket đúng Node và Alert khi có.
- [X] Operator phân công Technician đang hoạt động.
- [X] Technician chỉ xem/cập nhật Ticket được giao.
- [X] Luồng Ticket: mới tạo → đã phân công → đang xử lý → chờ duyệt → đã đóng.
- [X] Technician cập nhật tiến độ, kết quả và bằng chứng.
- [X] Operator duyệt đóng hoặc trả lại xử lý.
- [X] Lưu Ticket History.
- [x] API từ chối chuyển trạng thái sai hoặc vượt quyền.
- [X] Có giao diện danh sách, chi tiết, phân công và cập nhật Ticket.
- [x] Có kiểm thử toàn bộ luồng Alert → Ticket → xử lý → duyệt đóng.

---

## 6. Sprint 6 — Mobile AR, Audit và bàn giao

### Marker và Mobile AR

- [x] Có cấu trúc lưu Marker và liên kết Marker → Node.
- [x] Có migration quản lý Marker.
- [x] Có API tra cứu Node từ Marker theo phần Backend đã merge.
- [X] Chốt công nghệ Mobile AR và thiết bị Android kiểm thử.
- [X] Xây dựng ứng dụng Mobile Android.
- [X] Đăng nhập và quản lý phiên trên Mobile.
- [X] Xin quyền camera.
- [X] Quét QR hoặc ArUco theo thiết kế đã chốt.
- [X] Hiển thị đúng Node khi quét Marker hợp lệ.
- [X] Xử lý Marker sai, Marker bị vô hiệu hóa và mất mạng.
- [X] Hiển thị thông tin Node trong khung nhìn AR.
- [X] Hiển thị telemetry, trạng thái kết nối và Alert trong AR.
- [X] Technician xem Ticket liên quan đến Node đã quét.
- [X] Technician cập nhật Ticket từ Mobile.
- [ ] Hủy camera, timer và request khi rời màn hình.
- [ ] Có video quét Marker và hiển thị thông tin AR.


## 7. Kiểm thử tích hợp và nghiệm thu

### Kiểm thử kỹ thuật

- [X] `python -m pip check` đạt.
- [X] `alembic upgrade head` chạy trên database trống.
- [X] `alembic check` không phát hiện thay đổi schema chưa có migration.
- [x] Seed chạy được và không tạo trùng khi chạy lại.
- [x] Toàn bộ unittest Backend đạt.
- [X] `npm run lint` đạt.
- [X] `npm run build` đạt.
- [X] `git diff --check` sạch.
- [X] Không commit `.env`, `.env.migration`, `.venv`, `node_modules`, JWT hoặc Agent Key.

### Kịch bản nghiệp vụ cuối

- [x] Administrator quản lý tài khoản và cấu hình giám sát.
- [x] Operator xem tài sản và telemetry.
- [x] Agent gửi telemetry thật vào đúng Node.
- [x] Web hiển thị CPU, RAM, Disk và lịch sử.
- [x] Ngừng Agent: Web hiển thị dữ liệu cũ rồi mất kết nối đúng ngưỡng.
- [x] Agent gửi lại: Web hiển thị trạng thái phục hồi.
- [x] Vượt ngưỡng metric hoặc mất kết nối tạo Alert.
- [x] Operator xác nhận Alert.
- [x] Operator tạo Ticket và phân công Technician.
- [x] Technician xử lý Ticket trên Web hoặc Mobile.
- [x] Operator duyệt đóng Ticket.
- [x] Audit lưu đầy đủ các thao tác yêu cầu.
- [x] Mobile quét đúng Marker và hiển thị đúng Node.

