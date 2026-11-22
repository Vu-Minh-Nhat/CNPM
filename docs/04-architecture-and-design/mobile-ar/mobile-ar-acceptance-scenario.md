# Task 57 — Kịch bản nghiệm thu Mobile AR

## 1. Mục tiêu

Kịch bản này mô tả luồng demo Mobile AR xuyên suốt từ đăng nhập, nhận diện Node, xem dữ liệu, kiểm tra cảnh báo đến thao tác Ticket của Technician.

## 2. Điều kiện chuẩn bị

- Backend AR-IMMS đang hoạt động.
- Database PostgreSQL đang hoạt động.
- Mobile/Android đã cài phiên bản ứng dụng dùng để kiểm thử.
- Tài khoản Technician hợp lệ.
- Có ít nhất một Node đã tồn tại trong hệ thống.
- Có Marker được cấu hình và ánh xạ với Node.
- Camera của thiết bị hoạt động bình thường.
- Thiết bị có kết nối mạng.
- Có dữ liệu telemetry, trạng thái kết nối hoặc cảnh báo để kiểm tra nếu phạm vi triển khai có hỗ trợ.

## 3. Thiết bị kiểm thử

| STT | Thiết bị | Hệ điều hành | Camera | Marker | Trạng thái |
|---|---|---|---|---|---|
| 1 | Android Test Device 01 | Android phiên bản thực tế | Có | QR / ArUco | Pending |
| 2 | Android Test Device 02 | Android phiên bản thực tế | Có | QR / ArUco | Pending |

> Chỉ đánh dấu `PASS` đối với thiết bị, phiên bản Android và loại Marker đã thực sự được kiểm thử và có bằng chứng.

## 4. Kịch bản demo xuyên suốt

### Bước 1 — Đăng nhập

**Thao tác:**
1. Mở ứng dụng Mobile AR.
2. Nhập email và mật khẩu của Technician.
3. Thực hiện đăng nhập.

**Kết quả mong đợi:**
- Đăng nhập thành công.
- JWT được cấp cho phiên làm việc.
- Người dùng được đưa vào luồng Mobile AR phù hợp với quyền Technician.

**Bằng chứng:**
- Screenshot màn hình đăng nhập thành công.
- Screenshot màn hình AR Scanner.

**Test case:** `TC-MAR-01`

---

### Bước 2 — Mở AR Scanner và cấp quyền camera

**Thao tác:**
1. Mở chức năng AR Scanner.
2. Khi hệ điều hành yêu cầu quyền camera, chọn cho phép.

**Kết quả mong đợi:**
- Camera được mở.
- Màn hình Scanner hoạt động bình thường.
- Không hiển thị lỗi quyền camera.

**Bằng chứng:**
- Screenshot màn hình Scanner.

**Test case:** `TC-MAR-01`

---

### Bước 3 — Quét Marker

**Thao tác:**
1. Đưa camera hướng về Marker hợp lệ.
2. Giữ thiết bị đủ ổn định để hệ thống nhận diện Marker.

**Kết quả mong đợi:**
- Marker được nhận diện.
- Marker được ánh xạ tới Node tương ứng.
- Không hiển thị Node không liên quan.

**Bằng chứng:**
- Screenshot hoặc video quá trình nhận diện.
- Screenshot Node được nhận diện.

**Test case:** `TC-MAR-02`

---

### Bước 4 — Kiểm tra thông tin Node

**Thao tác:**
1. Sau khi Marker được nhận diện, mở thông tin Node.

**Kết quả mong đợi:**
- Hiển thị đúng định danh Node.
- Hiển thị vị trí thuộc phạm vi dữ liệu được hỗ trợ.
- Hiển thị telemetry nếu có dữ liệu.
- Hiển thị trạng thái kết nối.
- Hiển thị cảnh báo nếu Node có cảnh báo.

**Bằng chứng:**
- Screenshot màn hình Node Information.
- Screenshot telemetry.
- Screenshot trạng thái kết nối.
- Screenshot cảnh báo nếu có.

**Test case:** `TC-MAR-03`, `TC-MAR-04`, `TC-MAR-05`

---

### Bước 5 — Kiểm tra Ticket

**Thao tác:**
1. Technician mở Ticket liên quan đến Node.
2. Kiểm tra nội dung Ticket.
3. Thực hiện thao tác được phép đối với Ticket.
4. Lưu thay đổi.

**Kết quả mong đợi:**
- Technician chỉ nhìn thấy và thực hiện được thao tác thuộc quyền của mình.
- Dữ liệu Ticket được cập nhật thành công.
- Trạng thái mới được phản ánh trên Mobile.
- Backend nhận và lưu thay đổi.

**Bằng chứng:**
- Screenshot Ticket trước khi cập nhật.
- Screenshot Ticket sau khi cập nhật.
- Bằng chứng dữ liệu backend nếu cần.

**Test case:** `TC-MAR-06`

---

### Bước 6 — Kiểm tra phân quyền

**Thao tác:**
1. Đăng nhập bằng tài khoản Technician.
2. Truy cập luồng Mobile AR.
3. Kiểm tra các chức năng Ticket được phép sử dụng.
4. Kiểm tra hành vi khi gọi chức năng không thuộc quyền.

**Kết quả mong đợi:**
- Technician được phép thực hiện các chức năng thuộc phạm vi.
- Chức năng không được cấp quyền bị từ chối.
- Backend không cho phép vượt quyền chỉ bằng cách thay đổi giao diện Mobile.

**Bằng chứng:**
- Screenshot tài khoản và role.
- Screenshot kết quả truy cập.
- API response nếu có.

**Test case:** `TC-MAR-07`, `TC-MAR-08`

---

## 5. Kịch bản xử lý lỗi

### 5.1 Camera bị từ chối

**Thao tác:**
1. Từ chối quyền camera.
2. Mở lại AR Scanner.

**Kết quả mong đợi:**
- Ứng dụng không bị crash.
- Hiển thị thông báo yêu cầu cấp quyền camera.
- Người dùng biết cách khắc phục.

**Test case:** `TC-MAR-09`

---

### 5.2 Marker không hợp lệ

**Thao tác:**
1. Đưa camera tới Marker không tồn tại hoặc không được cấu hình.

**Kết quả mong đợi:**
- Marker không được ánh xạ nhầm sang Node.
- Hiển thị thông báo Marker không hợp lệ hoặc không tìm thấy Node.

**Test case:** `TC-MAR-10`

---

### 5.3 Mất mạng

**Thao tác:**
1. Đang sử dụng Mobile AR, ngắt kết nối mạng.
2. Thực hiện thao tác cần gọi backend.

**Kết quả mong đợi:**
- Ứng dụng không bị crash.
- Hiển thị trạng thái mất kết nối hoặc lỗi mạng.
- Không báo thành công giả cho thao tác chưa được backend xác nhận.
- Khi kết nối lại, người dùng có thể tiếp tục theo luồng được hỗ trợ.

**Test case:** `TC-MAR-11`

---

### 5.4 JWT hết hạn

**Thao tác:**
1. Sử dụng phiên đăng nhập đã hết hạn.
2. Thực hiện một thao tác cần xác thực.

**Kết quả mong đợi:**
- Backend từ chối request không còn hợp lệ.
- Mobile yêu cầu người dùng đăng nhập lại.
- Không cho tiếp tục thao tác bằng phiên hết hạn.

**Test case:** `TC-MAR-12`

---

### 5.5 Không đủ quyền

**Thao tác:**
1. Sử dụng tài khoản không có quyền thực hiện chức năng.
2. Gọi chức năng bị giới hạn.

**Kết quả mong đợi:**
- Request bị từ chối.
- Hiển thị thông báo không đủ quyền.
- Không thay đổi dữ liệu trái phép.

**Test case:** `TC-MAR-08`

---

## 6. Kết thúc nghiệm thu

Sau khi hoàn thành toàn bộ kịch bản:

1. Đối chiếu kết quả thực tế với ma trận truy vết.
2. Ghi nhận bằng chứng cho từng test case.
3. Đánh dấu `PASS`, `FAIL`, `Pending` hoặc `Out of scope`.
4. Ghi nhận các lỗi còn tồn tại.
5. Xác định người phụ trách xử lý các yêu cầu chưa đạt.
6. Chỉ kết luận nghiệm thu khi các yêu cầu bắt buộc đã có kết quả và bằng chứng phù hợp.

## 7. Tiêu chí kết luận

### PASS

Kịch bản được xem là đạt khi:

- Technician đăng nhập thành công.
- AR Scanner hoạt động.
- Marker hợp lệ được nhận diện đúng Node.
- Thông tin Node được hiển thị đúng trong phạm vi hỗ trợ.
- Telemetry, trạng thái kết nối và cảnh báo được hiển thị khi có dữ liệu.
- Technician thực hiện được thao tác Ticket được cấp quyền.
- Các trường hợp lỗi chính được xử lý an toàn.
- Không có hành vi vượt quyền.
- Có đầy đủ bằng chứng cho các yêu cầu bắt buộc.

### FAIL

Kịch bản được đánh dấu `FAIL` nếu có yêu cầu bắt buộc không đạt hoặc dữ liệu thực tế không khớp với yêu cầu.

### Pending

Kịch bản được đánh dấu `Pending` nếu chưa thể kiểm thử hoặc chưa có đủ bằng chứng.

### Out of scope

Kịch bản được đánh dấu `Out of scope` nếu chức năng không thuộc phạm vi đề tài hoặc không nằm trong cam kết nghiệm thu của Task 57.