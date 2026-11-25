# AR-IMMS — Backend Python

Backend AR-IMMS sử dụng Python, Flask, SQLAlchemy và PostgreSQL.

Backend cung cấp xác thực, quản lý tài khoản và tài sản, tiếp nhận telemetry,
cảnh báo và Ticket bảo trì.

## Yêu cầu

- Python và pip.
- PostgreSQL đang chạy.
- PowerShell trên Windows.
- Một database riêng cho môi trường phát triển.

Các lệnh dưới đây chạy trong thư mục `backend-python`.

## 1. Cài đặt

```powershell
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" -m pip check
```

## 2. Tạo database

Trong pgAdmin, tạo database phát triển, ví dụ:

```sql
CREATE DATABASE arimms_python;
```

Alembic tạo bảng trong database đã tồn tại; nó không tạo database.

## 3. Cấu hình môi trường

Tạo file cấu hình cá nhân:

```powershell
Copy-Item .env.example .env
notepad .env
```

Điền thông tin PostgreSQL của máy bạn:

```env
DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/arimms_python
JWT_SECRET=THAY_BANG_KHOA_BI_MAT
JWT_EXPIRES_IN_SECONDS=86400
CORS_ORIGINS=http://localhost:3001
TELEMETRY_AGENT_KEY=THAY_BANG_AGENT_KEY
TELEMETRY_AGENT_NODE_IDS=
TELEMETRY_STALE_AFTER_SECONDS=30
TELEMETRY_OFFLINE_AFTER_SECONDS=90
TELEMETRY_POLL_INTERVAL_SECONDS=5
```

Tạo JWT secret:

```powershell
& ".\.venv\Scripts\python.exe" -c "import secrets; print(secrets.token_hex(32))"
```

Tạo Agent Key:

```powershell
& ".\.venv\Scripts\python.exe" -c "import secrets; print(secrets.token_urlsafe(32))"
```

Dán mỗi giá trị vào biến tương ứng. Không dùng cùng một giá trị cho
`JWT_SECRET` và `TELEMETRY_AGENT_KEY`.

Nếu username hoặc password PostgreSQL có ký tự đặc biệt trong URL, cần mã hóa
chúng theo URL encoding.

`run.bat` hiện đọc `.env.migration`. Tạo file này nếu chưa có:

```powershell
Copy-Item .env .env.migration
```

Nếu `.env` và `.env.migration` trỏ tới database khác nhau, backend, migration,
seed và worker có thể dùng dữ liệu khác nhau. Luôn kiểm tra cấu hình trước khi
chạy.

Không commit `.env`, `.env.migration`, mật khẩu hoặc key lên Git.

## 4. Migration

Sau khi kiểm tra cấu hình database:

```powershell
& ".\.venv\Scripts\python.exe" -m alembic -x env_file=.env.migration upgrade head

& ".\.venv\Scripts\python.exe" -m alembic -x env_file=.env.migration current
```

Nếu migration thất bại, dừng lại và xử lý lỗi trước khi seed. Không dùng
`alembic stamp head` để bỏ qua lỗi schema.

## 5. Seed dữ liệu mẫu

Ví dụ khi `.env.migration` trỏ tới `arimms_python`:

```powershell
& ".\.venv\Scripts\python.exe" -m src.infrastructure.databases.seed `
  --env-file .env.migration `
  --expected-database arimms_python
```

Script yêu cầu đặt mật khẩu cho các tài khoản mẫu:

| Tài khoản | Vai trò |
| --- | --- |
| `admin@arimms.local` | Administrator |
| `operator@arimms.local` | Operator |
| `tech@arimms.local` | Technician |

Seed tạo cây tài sản mẫu gồm Site, Room, Rack, Node và Workload. Chạy lại seed
không tự đổi mật khẩu tài khoản đã có.

## 6. Cấu hình Agent

Lấy ID Node trong pgAdmin:

```sql
SELECT id, code, name
FROM nodes
ORDER BY code;
```

Điền UUID Node được phép gửi vào `.env.migration`:

```env
TELEMETRY_AGENT_KEY=AGENT_KEY_DA_TAO
TELEMETRY_AGENT_NODE_IDS=UUID_NODE
```

Agent cần dùng cùng key và Node ID. Xem
[hướng dẫn Agent](../agent/README.md).

## 7. Chạy Backend

```powershell
.\run.bat
```

Giữ terminal chạy và kiểm tra:

```text
http://localhost:5002/health
http://localhost:5002/docs/
```

Đây là Flask development server, dùng cho phát triển và kiểm thử cục bộ.

## 8. Chạy Alert Worker

Mở terminal khác tại `backend-python`:

```powershell
& ".\.venv\Scripts\python.exe" -m src.workers.alert_worker
```

Worker đánh giá Node và telemetry theo chu kỳ. Để tạo cảnh báo thực tế cần:

- Backend đang chạy.
- Agent gửi telemetry mới thành công.
- Có Alert Rule đang bật.
- Worker đang chạy.

Worker cần dùng cùng database với backend. Kiểm tra cấu hình môi trường mà
worker thực tế đọc trước khi chạy.

## 9. Kiểm thử Backend

Dùng database kiểm thử riêng đã migration và seed. Kiểm tra cấu hình test trước
khi chạy vì một số test ghi dữ liệu:

```powershell
& ".\.venv\Scripts\python.exe" -m unittest discover -s tests -p "test_*.py" -v
```

Nhập mật khẩu tài khoản seed khi chương trình yêu cầu.

## 10. API chính

| Chức năng | API |
| --- | --- |
| Health | `GET /health` |
| Đăng nhập | `POST /auth/login` |
| Tài khoản hiện tại | `GET /auth/me` |
| Tra cứu tài sản | `GET /assets` |
| Nhận telemetry | `POST /telemetry` |
| Danh sách cảnh báo | `GET /alerts` |
| Chi tiết cảnh báo | `GET /alerts/{id}` |
| Xác nhận cảnh báo | `POST /alerts/{id}/acknowledge` |
| Danh sách Rule | `GET /alerts/rules` |
| Tạo Rule | `POST /alerts/rules` |
| Cập nhật Rule | `PUT /alerts/rules/{id}` |
| Bật/tắt Rule | `PATCH /alerts/rules/{id}/active` |
| Ticket | Các route dưới `/tickets` |

API người dùng yêu cầu JWT và kiểm tra quyền ở backend. Endpoint telemetry
trong phiên bản này xác thực Agent bằng `X-Agent-Key`.
