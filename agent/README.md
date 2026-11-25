# AR-IMMS Collector Agent

Collector Agent thu thập CPU, RAM và Disk trên máy chạy Agent rồi gửi telemetry
đến backend theo chu kỳ.

Hướng dẫn này dành cho phiên bản xác thực bằng **Agent Key qua HTTP**.

## 1. Điều kiện

- Python và pip đã được cài.
- Backend đã chạy và kết nối đúng database.
- Database đã seed Node cần giám sát.
- Backend đã cấu hình `TELEMETRY_AGENT_KEY` và
  `TELEMETRY_AGENT_NODE_IDS`.

## 2. Cài đặt

Từ thư mục gốc dự án:

```powershell
cd agent
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

Kiểm tra:

```powershell
& ".\.venv\Scripts\python.exe" -c "import psutil, requests, dotenv; print('Agent dependencies: OK')"
```

Mỗi máy tự tạo `.venv`; không đưa `.venv` lên Git.

## 3. Lấy Node ID

Trong pgAdmin, chọn database backend đang dùng và chạy:

```sql
SELECT id, code, name
FROM nodes
ORDER BY code;
```

Copy UUID trong cột `id` của Node cần giám sát. Không dùng mã
`DEMO-NODE-01` thay cho UUID.

## 4. Cấu hình backend

Backend cần có các biến:

```env
TELEMETRY_AGENT_KEY=KEY_BI_MAT
TELEMETRY_AGENT_NODE_IDS=UUID_NODE
```

Nếu backend được chạy bằng `run.bat`, kiểm tra cấu hình trong file mà
launcher đọc, hiện là `backend-python/.env.migration`.

Có thể tạo key bằng Python tại thư mục `backend-python`:

```powershell
& ".\.venv\Scripts\python.exe" -c "import secrets; print(secrets.token_urlsafe(32))"
```

Khởi động lại backend sau khi thay cấu hình.

## 5. Cấu hình Agent

Tại thư mục `agent`, tạo file cá nhân:

```powershell
Copy-Item .env.example .env
notepad .env
```

Ví dụ:

```env
BACKEND_URL=http://localhost:5002
TELEMETRY_ENDPOINT=/telemetry

NODE_ID=UUID_NODE
AGENT_KEY=KEY_BI_MAT

SEND_INTERVAL_SECONDS=5
REQUEST_TIMEOUT_SECONDS=5
MAX_RETRIES=3
RETRY_DELAY_SECONDS=2
```

- `BACKEND_URL` phải khớp địa chỉ backend đang chạy.
- `NODE_ID` phải nằm trong `TELEMETRY_AGENT_NODE_IDS` của backend.
- `AGENT_KEY` phải giống `TELEMETRY_AGENT_KEY` của backend.
- Không đưa mật khẩu PostgreSQL hoặc JWT secret vào Agent.

Nếu backend ở máy khác, `localhost` không trỏ tới máy backend; cần dùng địa chỉ
và cấu hình mạng phù hợp. HTTP + Agent Key trong ví dụ này dành cho môi trường
kiểm thử nội bộ, không đưa key qua mạng không tin cậy.

## 6. Chạy Agent

Tại thư mục `agent`:

```powershell
.\run.bat
```

Hoặc:

```powershell
& ".\.venv\Scripts\python.exe" agent.py
```

Giữ terminal mở. Dừng bằng `Ctrl + C`.

## 7. Kiểm tra dữ liệu

Trong pgAdmin:

```sql
SELECT node_id, measured_at, received_at,
       cpu_percent, memory_percent, disk_percent
FROM node_telemetry
ORDER BY received_at DESC
LIMIT 5;
```

Nếu `received_at` liên tục cập nhật, backend đang lưu telemetry mới.

Để tạo cảnh báo còn cần rule đang bật và Alert Worker chạy riêng. Xem
[README Backend](../backend-python/README.md).

## 8. Lỗi thường gặp

| Lỗi | Cách kiểm tra |
| --- | --- |
| Chưa có `.venv` | Tạo venv và cài dependencies trong thư mục `agent`. |
| Chưa cấu hình `AGENT_KEY` | Kiểm tra `agent/.env` có key và đã lưu file. |
| HTTP 401 | Đối chiếu Agent Key với key backend thực sự đang đọc. |
| HTTP 403 | Kiểm tra `NODE_ID` có nằm trong danh sách backend cho phép. |
| Connection refused | Kiểm tra backend đang chạy và `BACKEND_URL` đúng host/cổng. |
| Không có Alert | Kiểm tra telemetry mới, rule đang bật và Alert Worker. |

Không commit `.env`, `.venv` hoặc Agent Key lên Git.
