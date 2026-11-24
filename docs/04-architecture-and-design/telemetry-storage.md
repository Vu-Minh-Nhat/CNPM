# AI-43 — Lưu trữ Telemetry

## Phạm vi

Bổ sung model, migration và repository lưu telemetry cấp Node.
API tiếp nhận, Collector Agent và giao diện thuộc các task khác.

## Đặc tả tạm thời

Một bản tin chứa CPU, RAM và disk của một Node.
Thiết kế cần được nhóm thống nhất khi hoàn thiện hợp đồng dữ liệu Task 1.

Bảng `node_telemetry`:

| Trường | Ý nghĩa |
| --- | --- |
| id | UUID bản ghi do Backend tạo |
| message_id | UUID bản tin, giữ nguyên khi retry |
| node_id | Khóa ngoại tới nodes.id |
| measured_at | Thời điểm đo, có múi giờ |
| received_at | Thời điểm database tạo bản ghi |
| cpu_percent | CPU sử dụng, từ 0–100% |
| memory_percent | RAM sử dụng, từ 0–100% |
| disk_percent | Disk sử dụng, từ 0–100% |

Các trường đều bắt buộc.

## Ràng buộc và truy vấn

- Unique: node_id + message_id.
- Khóa ngoại tới Node sử dụng ON DELETE RESTRICT.
- Database kiểm tra ba metric nằm trong khoảng 0–100.
- Index gồm node_id, measured_at, received_at và id.
- Timestamp được repository chuẩn hóa về UTC.

## Repository

- save: lưu mẫu mới; bản tin trùng cùng nội dung trả bản ghi cũ.
- Cùng định danh nhưng khác nội dung: báo xung đột, không ghi đè.
- get_latest: giảm dần theo measured_at, received_at và id.
- list_history: start <= measured_at < end.
- Lịch sử tăng dần theo measured_at, received_at và id.
- Limit mặc định 100, cho phép từ 1 đến 1000.

Chống trùng sử dụng unique constraint và INSERT ON CONFLICT.

## Migration

- Revision trước: 7d8caeeeb709.
- Revision mới: 1663b308482e.
- Chỉ bổ sung bảng và index telemetry.
- Migration khởi tạo cũ được giữ nguyên.

## Kiểm thử

Chạy tại backend-python, dùng database arimms_python_check:

```powershell
& ".\.venv\Scripts\python.exe" -m unittest discover -s tests -p "test_telemetry_repository.py" -v
```

Kết quả ngày 11/11/2026:

- 14 kiểm thử telemetry PASS.
- Toàn bộ 27 kiểm thử Backend PASS, thời gian 7.953 giây.
- Alembic check: No new upgrade operations detected.

Kiểm thử bao phủ lưu dữ liệu, gửi trùng, xung đột nội dung,
khóa ngoại, metric sai, timestamp, dữ liệu mới nhất, lịch sử,
phân tách Node và gửi trùng đồng thời.

Test tạo Node AI43-* riêng và dọn dữ liệu sau mỗi test.

## Giới hạn

Chưa triển khai telemetry cấp Workload, API tiếp nhận,
xác thực Agent, giao diện, phân vùng hoặc chính sách lưu giữ dữ liệu.