# Kiểm thử AI-41 — Danh sách và chi tiết tài sản

## 1. Phạm vi

- Tích hợp GET /assets.
- Hiển thị mã, tên, serial và vị trí Node.
- Xem chi tiết Rack → Room → Site và Workload.
- Tìm kiếm, lọc theo Site trên dữ liệu đã tải.
- Xử lý lỗi, dữ liệu thiếu và kết quả rỗng.
- Không cung cấp thao tác tạo, sửa hoặc xóa.

## 2. Môi trường

- Frontend: http://localhost:3001.
- Backend: http://localhost:3000.
- Database có dữ liệu seed.
- Nhánh: codex/AI-41-assets.

Ghi bổ sung ngày kiểm tra và commit khi bàn giao.

## 3. Kết quả

| Trường hợp | Kết quả |
|---|---|
| npm run lint | Đạt |
| npm run build | Đạt |
| Hiển thị DEMO-NODE-01 | Đạt |
| Hiển thị Rack, Room, Site và Workload đã seed | Điền sau khi xác nhận |
| Mở và đóng khung chi tiết | Điền sau khi xác nhận |
| Tìm kiếm và lọc kết hợp | Điền sau khi xác nhận |
| Từ khóa không khớp | Điền sau khi xác nhận |
| Cả ba vai trò xem được danh sách và chi tiết | Điền sau khi xác nhận |
| Không gọi API chi tiết khi chọn Node | Điền sau khi xác nhận |
| Hiển thị lỗi và phục hồi sau gián đoạn Backend | Đạt |
| Phản hồi danh sách rỗng | Đạt — dữ liệu giả lập |
| Thiếu serial, quan hệ vị trí và Workload rỗng | Điền sau khi xác nhận |

Chỉ đổi thành Đạt đối với trường hợp đã kiểm tra thực tế.

## 4. Phương pháp kiểm tra dữ liệu biên

Danh sách rỗng và dữ liệu thiếu được giả lập
bằng cách thay phản hồi fetch trong tab trình duyệt.

Không xóa hoặc sửa database để tạo các trường hợp này.
Tải lại toàn bộ trang để khôi phục dữ liệu thật.

## 5. Giới hạn

- Tìm kiếm và lọc chỉ áp dụng trên danh sách đã tải.
- Chi tiết lấy từ dữ liệu GET /assets.
- Không gọi GET /assets/:id.
- Không triển khai chức năng tạo, sửa hoặc xóa.