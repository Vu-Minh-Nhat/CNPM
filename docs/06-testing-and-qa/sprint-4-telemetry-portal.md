# Kiểm thử giám sát Telemetry trên Web Portal

## Phạm vi

- Hiển thị CPU, RAM, Disk và thời điểm đo theo Node.
- Tra cứu lịch sử theo khoảng thời gian 5, 15 và 60 phút.
- Tự cập nhật dữ liệu mà không tải lại toàn bộ trang.
- Phân biệt Node chưa từng gửi, đang kết nối và mất kết nối.
- Phân biệt dữ liệu còn mới và dữ liệu đã cũ.

## Môi trường

- Backend: Flask, cổng 5002.
- Frontend: Next.js, cổng 3001.
- Database kiểm thử: arimms_python_check.
- Agent thu thập tài nguyên của máy chạy thử nghiệm.
- Node được theo dõi: DEMO-NODE-01.

## Quy tắc trạng thái

- Chưa từng nhận dữ liệu: chưa có lần tiếp nhận hợp lệ.
- Đang kết nối: lần tiếp nhận hợp lệ gần nhất cách hiện tại
  không quá 90 giây.
- Mất kết nối: quá 90 giây không nhận được bản tin hợp lệ.
- Dữ liệu còn mới: thời điểm đo cách hiện tại không quá 30 giây.
- Dữ liệu đã cũ: thời điểm đo cách hiện tại quá 30 giây.
- Trạng thái được tính lại khi đọc dữ liệu, kể cả khi Agent
  không gửi bản tin mới.
- Web đọc dữ liệu mới nhất theo chu kỳ cấu hình, mặc định 5 giây.

## Kết quả kiểm tra kỹ thuật

| Kiểm tra | Kết quả |
| --- | --- |
| Bộ kiểm thử Python hiện có | Đạt |
| Alembic check | Không phát hiện thay đổi schema chưa có migration |
| Frontend lint | Đạt |
| Frontend build | Đạt |
| Git diff --check | Đạt |

## Kiểm thử giao diện và tích hợp

| Tình huống | Kết quả mong đợi | Kết quả |
| --- | --- | --- |
| Node chưa từng gửi | Hiển thị chưa từng nhận và chưa có dữ liệu | Đạt |
| Agent gửi thành công | Hiển thị metric, timestamp và trạng thái đang kết nối | Đạt |
| Xem lịch sử | Hiển thị các mẫu thực nhận từ API | Đạt |
| Đổi khoảng 5/15/60 phút | Truy vấn và hiển thị đúng khoảng đã chọn | Đạt |
| Agent ngừng gửi quá 30 giây | Giữ mẫu cuối và đánh dấu dữ liệu cũ | Đạt |
| Agent ngừng gửi quá 90 giây | Hiển thị mất kết nối | Đạt |
| Agent gửi lại | Trở lại đang kết nối sau lượt cập nhật | Đạt |
| Chuyển Node hoặc đóng chi tiết | Hủy request và timer của phiên cũ | Đạt |
| API lỗi | Hiển thị lỗi; dữ liệu giữ lại được nhận diện rõ | Đạt |
| Phiên đăng nhập hết hạn | Xử lý theo cơ chế xác thực của Web | Đạt |


## Bằng chứng bàn giao

Đính kèm trên Jira:

1. Ảnh Node chưa từng nhận dữ liệu.
2. Ảnh đang kết nối, có metric và biểu đồ.
3. Ảnh dữ liệu cũ và mất kết nối, còn timestamp cuối.
4. Ảnh kết nối lại sau khi khởi động Agent.
5. Kết quả kiểm thử Python, Alembic check, lint và build.

Không đưa API key, mật khẩu hoặc token vào bằng chứng.