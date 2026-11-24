# Collector Agent — CPU, RAM và Disk Telemetry

## 1. Mục đích

Collector Agent là chương trình Python chạy trên máy testbed để thu thập dữ liệu sử dụng tài nguyên hệ thống gồm:

- CPU usage (%)
- RAM usage (%)
- Disk usage (%)

Agent gửi dữ liệu telemetry về Backend theo chu kỳ cấu hình.

## 2. Cấu trúc

```text
agent/
├── agent.py
├── config.py
├── requirements.txt
├── .env.example
├── .env
└── README.md
```

## 3. Yêu cầu môi trường

- Python 3.x
- Backend đang chạy tại địa chỉ được cấu hình trong `.env`
- PostgreSQL đã được cấu hình ở Backend

## 4. Cài đặt

Mở Terminal tại thư mục `agent`:

```powershell
python -m pip install -r requirements.txt
```

Kiểm tra dependencies:

```powershell
python -c "import psutil, requests, dotenv; print('Agent dependencies OK')"
```

## 5. Cấu hình

Tạo file `.env` từ `.env.example` và cấu hình các biến:

```env
BACKEND_URL=http://localhost:5000
TELEMETRY_ENDPOINT=/telemetry

NODE_ID=
DATABASE_URL=
JWT_SECRET=
AUTH_TOKEN=

SEND_INTERVAL_SECONDS=5
REQUEST_TIMEOUT_SECONDS=5
MAX_RETRIES=3
RETRY_DELAY_SECONDS=2
```

Không commit file `.env` lên Git vì file này chứa thông tin cấu hình và thông tin xác thực.

## 6. Chạy Agent

Đảm bảo Backend đang chạy trước.

Tại thư mục `agent`:

```powershell
python agent.py
```

Khi chạy thành công, Agent sẽ hiển thị thông tin thu thập CPU, RAM và Disk, sau đó gửi telemetry về Backend.

Ví dụ:

```text
Collector Agent started.
Backend=http://localhost:5000/telemetry | interval=5.0s
Collected telemetry: CPU=23.10%, RAM=76.70%, Disk=77.90%
Telemetry sent successfully: message_id=...
```

## 7. Cơ chế gửi dữ liệu

Mỗi telemetry message có:

- `message_id`: UUID duy nhất cho message
- `node_id`: định danh Node
- `measured_at`: thời điểm đo
- `cpu_percent`: CPU usage (%)
- `memory_percent`: RAM usage (%)
- `disk_percent`: Disk usage (%)

Agent sử dụng HTTP POST để gửi dữ liệu đến:

```text
POST /telemetry
```

## 8. Timeout và Retry

Agent được cấu hình:

```env
REQUEST_TIMEOUT_SECONDS=5
MAX_RETRIES=3
RETRY_DELAY_SECONDS=2
```

Nếu kết nối Backend thất bại, Agent thử lại tối đa 3 lần.

Mỗi lần retry sử dụng cùng `message_id` và `measured_at` của telemetry message đó.

## 9. Kiểm tra dữ liệu trong Database

Telemetry được lưu trong bảng:

```text
node_telemetry
```

Có thể kiểm tra các bản ghi mới nhất bằng PostgreSQL:

```sql
SELECT
    message_id,
    node_id,
    measured_at,
    cpu_percent,
    memory_percent,
    disk_percent,
    received_at
FROM node_telemetry
ORDER BY received_at DESC
LIMIT 5;
```

## 10. Dừng Agent

Trong Terminal đang chạy Agent:

```text
Ctrl + C
```

## 11. Kết quả kiểm thử

Agent đã được kiểm thử trên máy testbed với kết quả:

- Thu thập được CPU thực tế.
- Thu thập được RAM thực tế.
- Thu thập được Disk thực tế.
- Gửi telemetry thành công đến Backend.
- Backend lưu dữ liệu vào PostgreSQL.
- Mỗi message có `message_id` riêng.
- Dữ liệu trong `node_telemetry` có đầy đủ thời gian đo và các chỉ số CPU/RAM/Disk.

Ví dụ dữ liệu kiểm thử:

```text
CPU: 22.4%
RAM: 77.2%
Disk: 79.8%
```