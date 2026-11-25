# Bàn giao AR-IMMS testbed

Tài liệu này mô tả phạm vi demo, không xác nhận triển khai production. Trước nghiệm thu, ghi commit, môi trường, kết quả và bằng chứng thực tế.

## Khởi động

1. Tạo database và chạy migration, seed theo [backend](../../backend-python/README.md). Đảm bảo backend và worker dùng cùng database; không đưa mật khẩu hoặc khóa vào Git.
2. Chạy backend: tại `backend-python`, `.\run.bat`. Với điện thoại trong mạng testbed, có thể dùng `.\run_mobile.bat` theo hướng dẫn mobile. Kiểm tra `/health` và `/docs/`.
3. Mở terminal backend khác chạy `& ".\.venv\Scripts\python.exe" -m src.workers.alert_worker`. Kiểm tra worker đọc đúng database; giữ tiến trình mở.
4. Thiết lập Node ID và Agent Key, khởi động Agent theo [agent](../../agent/README.md). Phải có rule được bật và telemetry phù hợp để phát sinh cảnh báo.
5. Chạy web theo [frontend](../../frontend/README.md); chạy mobile theo [mobile](../../mobile/README.md). Administrator tạo marker QR gắn Node; quét bằng Technician.

## Demo

Ghi lại phiên bản, Node và thời gian; thực hiện Agent → telemetry → cảnh báo → Operator tạo/phân công ticket → Technician quét Node và xử lý → gửi duyệt → Operator đóng trên web. Quay video và đối chiếu ID, trạng thái và lịch sử. Nếu lỗi: kiểm tra health, tiến trình worker/Agent, kết nối LAN, rule và quyền; ghi nhận lỗi thay vì thay dữ liệu để mô phỏng thành công.

## Sao lưu và khôi phục thử nghiệm PostgreSQL

Chỉ thực hiện trên database được phép, bằng tài khoản có quyền phù hợp. Dùng `pg_dump` của phiên bản PostgreSQL tương thích; đặt mật khẩu qua cơ chế bảo mật của PostgreSQL, không ghi vào tài liệu hoặc shell history.

```powershell
pg_dump -h localhost -U postgres -Fc -f arimms-backup.dump TEN_DATABASE
```

Kiểm tra bản sao bằng cách tạo **database thử nghiệm mới trống**, sau đó khôi phục vào database đó:

```powershell
pg_restore -h localhost -U postgres -d TEN_DATABASE_THU_NGHIEM arimms-backup.dump
```

Đối chiếu bảng, số lượng dữ liệu cần thiết và migration hiện hành. Không khôi phục đè database đang dùng. Bản sao có thể chứa dữ liệu nhạy cảm: bảo vệ quyền truy cập và quy định nơi lưu/thời gian lưu theo nhóm. Các lệnh này chưa được kiểm thử trên môi trường của người nghiệm thu.

## Mục cần xác nhận trước bàn giao

- Chạy lại migration và seed trên database trống; clone sạch trên máy khác; ghi lại phiên bản Node/Python/PostgreSQL và kết quả.
- Lưu ảnh/video, kết quả build và kiểm thử, báo cáo và phiên bản commit. Kiểm tra file mẫu không có bí mật thực.
- Audit hiện mới tra cứu lịch sử ticket và alert, chưa bao phủ thay đổi Marker/rule; kiểm tra quyền và chính sách toàn vẹn còn thiếu.
- NFR-07 hiện yêu cầu mTLS; bản Agent đang dùng Agent Key. Việc tạm bỏ mTLS cần được nhóm phê duyệt hoặc chấp nhận là chưa đáp ứng.
- Lớp phủ camera chưa được xác nhận bám marker trong không gian AR; bằng chứng ticket dưới dạng văn bản/đường dẫn, chưa xác nhận bảo vệ tài nguyên bên ngoài.
- Chưa xác nhận build/cài APK, khôi phục backup hoặc triển khai production.
