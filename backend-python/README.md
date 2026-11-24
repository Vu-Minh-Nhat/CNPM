# AR-IMMS — Backend Python

Backend của hệ thống AR-IMMS được phát triển bằng Python, Flask,
SQLAlchemy và PostgreSQL theo cấu trúc Clean Architecture.

Backend hiện cung cấp xác thực JWT, phân quyền, quản lý tài khoản,
quản lý Site/Room/Rack/Server và tra cứu cây tài sản.

## 1. Yêu cầu môi trường

- Python 3.15.2 — phiên bản đã kiểm thử.
- PostgreSQL đang hoạt động.
- Git.
- PowerShell trên Windows.

Các lệnh bên dưới được chạy tại thư mục `backend-python`.

## 2. Cấu trúc

```text
backend-python/
├── migrations/              # Các phiên bản migration Alembic
├── src/
│   ├── api/                 # Controller, middleware, phản hồi lỗi
│   ├── domain/              # Model nghiệp vụ và các interface
│   ├── infrastructure/      # SQLAlchemy, repository, bảo mật
│   ├── services/            # Xử lý nghiệp vụ
│   ├── create_app.py        # Khởi tạo ứng dụng Flask
│   ├── dependency_container.py
│   └── app.py               # Điểm chạy Backend
├── tests/                   # Kiểm thử tự động
├── .env.example             # Mẫu cấu hình
├── alembic.ini
└── requirements.txt
```

## 3. Cài đặt dependencies

```powershell
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" -m pip check
```

Kết quả kiểm tra mong đợi:

```text
No broken requirements found.
```

## 4. Tạo database phát triển

Trong pgAdmin, tạo một database trống:

```text
arimms_python
```

Migration tạo bảng trong database đã tồn tại; migration không tạo
database PostgreSQL.

Không chạy migration khởi tạo này trên database cũ đã có các bảng
được quản lý bằng TypeORM.

## 5. Cấu hình môi trường

Tạo file cấu hình nếu chưa có:

```powershell
Copy-Item .env.example .env
```

Cập nhật `.env`:

```dotenv
DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/arimms_python
JWT_SECRET=
JWT_EXPIRES_IN_SECONDS=86400
CORS_ORIGINS=http://localhost:3001,http://localhost:3002
```

- `DATABASE_URL`: thông tin kết nối PostgreSQL.
- `JWT_SECRET`: khóa ký JWT, tối thiểu 32 byte.
- `JWT_EXPIRES_IN_SECONDS`: thời gian hiệu lực token, tính bằng giây.
- `CORS_ORIGINS`: các origin Frontend được phép gọi API,
  phân cách bằng dấu phẩy.

Tạo khóa JWT:

```powershell
& ".\.venv\Scripts\python.exe" -c "import secrets; print(secrets.token_hex(32))"
```

Dán giá trị nhận được vào `JWT_SECRET`.

Nếu username hoặc password chứa ký tự đặc biệt trong URL,
cần mã hóa phần thông tin đó theo URL encoding.

Không đưa `.env`, `.env.migration`, mật khẩu hoặc JWT lên Git.

## 6. Khởi tạo bảng bằng migration

```powershell
& ".\.venv\Scripts\python.exe" -m alembic upgrade head
& ".\.venv\Scripts\python.exe" -m alembic current
```

Database gồm các bảng nghiệp vụ:

- roles
- users
- sites
- rooms
- racks
- nodes
- workloads

Bảng `alembic_version` lưu phiên bản migration hiện tại.

Thành viên nhận mã nguồn chỉ cần `upgrade head`, không cần chạy lại
`alembic init` hoặc tạo migration khởi tạo mới.

## 7. Tạo dữ liệu mẫu

```powershell
& ".\.venv\Scripts\python.exe" -m src.infrastructure.databases.seed --expected-database arimms_python
```

Nhập và xác nhận mật khẩu chung cho các tài khoản mẫu mới.

| Email | Vai trò |
| --- | --- |
| admin@arimms.local | Administrator |
| operator@arimms.local | Operator |
| tech@arimms.local | Technician |

Cây tài sản mẫu:

```text
DEMO-SITE
└── ROOM-01
    └── RACK-01
        └── DEMO-NODE-01
            └── DEMO-WORKLOAD-01
```

Seed chỉ thêm dữ liệu còn thiếu. Chạy lại không đặt lại mật khẩu
hoặc vai trò của tài khoản đã tồn tại.

## 8. Chạy Backend

```powershell
.\run.bat
```

Địa chỉ mặc định:

```text
http://localhost:5002
```

Kiểm tra hoạt động:

```powershell
Invoke-RestMethod -Uri "http://localhost:5002/health"
```

Kết quả có:

```json
{
  "status": "ok"
}
```

Lệnh chạy hiện tại dùng Flask development server, phục vụ phát triển
và kiểm thử cục bộ. Cấu hình triển khai production là công việc riêng.

## 9. Kết nối Frontend

Trong `frontend/.env.local`:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:5002
```

Khởi động lại Frontend sau khi sửa biến môi trường:

```powershell
npm run dev -- --port 3001
```

Chạy lệnh Frontend tại thư mục `frontend`.

## 10. API hiện có

| Nhóm | Endpoint |
| --- | --- |
| Kiểm tra hoạt động | GET /health |
| Đăng nhập | POST /auth/login |
| Tài khoản hiện tại | GET /auth/me |
| Danh sách tài khoản | GET /users |
| Tạo tài khoản | POST /users |
| Đổi vai trò | PATCH /users/{id}/role |
| Tra cứu cây tài sản | GET /assets |
| Ticket bảo trì | GET, POST /tickets; GET /tickets/{ticket_id}; GET /tickets/{ticket_id}/history |
| Quy trình ticket | POST /tickets/{ticket_id}/assign, /start, /submit, /approve-close, /return; PATCH /tickets/{ticket_id}/work |
| Site | GET, POST /sites; GET, PATCH, DELETE /sites/{id} |
| Room | GET, POST /rooms; GET, PATCH, DELETE /rooms/{id} |
| Rack | GET, POST /racks; GET, PATCH, DELETE /racks/{id} |
| Server | GET, POST /servers; GET, PATCH, DELETE /servers/{id} |

API yêu cầu xác thực nhận header:

```text
Authorization: Bearer <accessToken>
```

Phân quyền chính:

- Administrator: quản trị tài khoản; xem, tạo, sửa, xóa tài sản.
- Operator: xem, tạo và sửa tài sản; không xóa hoặc quản trị tài khoản.
- Technician: xem tài sản; không tạo, sửa, xóa hoặc quản trị tài khoản.
- Operator quản lý ticket; Technician chỉ xem và cập nhật ticket được phân công.

Mã lỗi thường gặp:

| HTTP status | Ý nghĩa |
| --- | --- |
| 400 | Dữ liệu đầu vào không hợp lệ |
| 401 | Chưa xác thực hoặc thông tin xác thực không hợp lệ |
| 403 | Không đủ quyền |
| 404 | Không tìm thấy dữ liệu |
| 409 | Trùng dữ liệu hoặc xung đột quan hệ |

### OpenAPI và Swagger UI

- Swagger UI: http://localhost:5002/docs/
- Đặc tả OpenAPI: http://localhost:5002/openapi.json

Để thử API được bảo vệ:

1. Gọi POST /auth/login bằng tài khoản hợp lệ.
2. Copy giá trị accessToken.
3. Nhấn Authorize và dán token, không thêm chữ Bearer.
4. Thực hiện các yêu cầu theo quyền của tài khoản.

### Chạy thử quy trình Ticket bảo trì

Thực hiện tại PowerShell, với PostgreSQL, `.env`, dependencies và migration
đã chuẩn bị theo các mục phía trên. Nếu cần dữ liệu demo, tạo seed trước:

```powershell
& ".\.venv\Scripts\python.exe" -m src.infrastructure.databases.seed --expected-database arimms_python
```

Khởi động Backend trong một cửa sổ PowerShell:

```powershell
.\run.bat
```

Trong cửa sổ PowerShell khác, đăng nhập Operator và Technician. Thay
`__MAT_KHAU_SEED__` bằng mật khẩu đã đặt khi seed:

```powershell
$base = "http://localhost:5002"
$password = "__MAT_KHAU_SEED__"
$operatorLogin = Invoke-RestMethod -Method Post -Uri "$base/auth/login" `
    -ContentType "application/json" `
    -Body (@{ email = "operator@arimms.local"; password = $password } | ConvertTo-Json)
$technicianLogin = Invoke-RestMethod -Method Post -Uri "$base/auth/login" `
    -ContentType "application/json" `
    -Body (@{ email = "tech@arimms.local"; password = $password } | ConvertTo-Json)
$operatorHeaders = @{ Authorization = "Bearer $($operatorLogin.accessToken)" }
$technicianHeaders = @{ Authorization = "Bearer $($technicianLogin.accessToken)" }
$technician = Invoke-RestMethod -Uri "$base/auth/me" -Headers $technicianHeaders
```

Lấy Node mẫu, tạo ticket, rồi phân công cho Technician:

```powershell
$nodes = Invoke-RestMethod -Uri "$base/assets" -Headers $operatorHeaders
$node = $nodes | Where-Object { $_.code -eq "DEMO-NODE-01" } | Select-Object -First 1
$ticket = Invoke-RestMethod -Method Post -Uri "$base/tickets" `
    -Headers $operatorHeaders -ContentType "application/json" `
    -Body (@{
        node_id = $node.id
        title = "Kiểm tra thiết bị"
        description = "Kiểm tra tình trạng Node và ghi nhận kết quả."
    } | ConvertTo-Json)
$ticket = Invoke-RestMethod -Method Post -Uri "$base/tickets/$($ticket.id)/assign" `
    -Headers $operatorHeaders -ContentType "application/json" `
    -Body (@{ assigned_to = $technician.userId; version = $ticket.version } | ConvertTo-Json)
```

Technician bắt đầu xử lý, cập nhật tiến độ và gửi kết quả; Operator duyệt đóng:

```powershell
$ticket = Invoke-RestMethod -Method Post -Uri "$base/tickets/$($ticket.id)/start" `
    -Headers $technicianHeaders -ContentType "application/json" `
    -Body (@{ version = $ticket.version } | ConvertTo-Json)
$ticket = Invoke-RestMethod -Method Patch -Uri "$base/tickets/$($ticket.id)/work" `
    -Headers $technicianHeaders -ContentType "application/json" `
    -Body (@{
        version = $ticket.version
        progress = 75
        work_notes = "Đã kiểm tra thiết bị."
        evidence = "Ảnh kiểm tra được lưu trong hồ sơ vận hành."
    } | ConvertTo-Json)
$ticket = Invoke-RestMethod -Method Post -Uri "$base/tickets/$($ticket.id)/submit" `
    -Headers $technicianHeaders -ContentType "application/json" `
    -Body (@{ version = $ticket.version; result = "Thiết bị hoạt động bình thường." } | ConvertTo-Json)
$ticket = Invoke-RestMethod -Method Post -Uri "$base/tickets/$($ticket.id)/approve-close" `
    -Headers $operatorHeaders -ContentType "application/json" `
    -Body (@{ version = $ticket.version; note = "Đã kiểm tra kết quả." } | ConvertTo-Json)
```

Để xem lịch sử hoặc thử nhánh trả lại, gọi `GET /tickets/{ticket_id}/history`
hoặc `POST /tickets/{ticket_id}/return` với body có `version` và `reason`.
Mỗi lần ghi phải dùng `version` mới nhất trong phản hồi; nếu phiên bản đã cũ,
API trả `409 Conflict`. `alert_id` có thể thêm vào payload tạo ticket, nhưng
phải thuộc cùng Node. Bằng chứng hiện được gửi dưới dạng văn bản/tham chiếu,
không phải tệp tải lên.

Chạy kiểm thử tự động của ticket (không cần khởi động server riêng):

```powershell
& ".\.venv\Scripts\python.exe" -m unittest discover -s tests -p "test_ticket_service.py" -v
```

Swagger gọi API trên cùng host và cổng đang mở tài liệu.

## 11. Chuẩn bị database kiểm thử riêng

Tạo database trống trong pgAdmin:

```text
arimms_python_check
```

Tạo file cấu hình kiểm thử nếu chưa có:

```powershell
Copy-Item .env .env.migration
```

Trong `.env.migration`, đổi database cuối `DATABASE_URL` thành
`arimms_python_check`. Giữ thông tin kết nối PostgreSQL phù hợp.

Khởi tạo cấu trúc và dữ liệu:

```powershell
& ".\.venv\Scripts\python.exe" -m alembic -x env_file=.env.migration upgrade head
& ".\.venv\Scripts\python.exe" -m src.infrastructure.databases.seed --env-file .env.migration --expected-database arimms_python_check
```
### Kiểm thử CRUD tài sản

```powershell
& ".\.venv\Scripts\python.exe" -m unittest discover -s tests -p "test_asset_crud.py" -v
```

Kiểm tra tạo, cập nhật, đọc và xóa Site/Room/Rack/Server;
chặn xóa tài sản cha, từ chối Rack không tồn tại và mã Server trùng.
Dữ liệu do ca kiểm thử tạo được dọn sau khi chạy.

### Chạy toàn bộ kiểm thử Backend

```powershell
& ".\.venv\Scripts\python.exe" -m unittest discover -s tests -p "test_*.py" -v
```

Các kiểm thử dùng database `arimms_python_check`.
Nhập mật khẩu tài khoản seed khi chương trình yêu cầu.

## 12. Chạy kiểm thử API tự động

```powershell
& ".\.venv\Scripts\python.exe" -m unittest discover -s tests -p "test_api_smoke.py" -v
```

Nhập mật khẩu chung của ba tài khoản trong database kiểm thử.

Bộ kiểm thử sử dụng Flask test client và PostgreSQL thật;
không cần khởi động server Flask riêng.

Các nội dung kiểm tra:

- Thông tin tài khoản hiện tại.
- Danh sách tài khoản và không trả về mật khẩu.
- Node mẫu và quan hệ Rack, Room, Site, Workload.
- Yêu cầu thiếu hoặc sai token.
- Quyền quản trị tài khoản của Operator và Technician.
- Dữ liệu quản trị tài khoản rỗng.
- Đăng nhập sai mật khẩu.

Kết quả đã ghi nhận: 8 tests PASS.

Bộ test giả định ba tài khoản seed vẫn hoạt động, giữ vai trò ban đầu
và dùng cùng mật khẩu đã đặt khi seed.

## 13. Phạm vi hiện tại

Backend lõi đã được chuyển sang Flask và kiểm tra với database mới
được khởi tạo bằng migration Python.

Các chức năng telemetry, cảnh báo, lịch sử dữ liệu, ticket và hỗ trợ AR
được phát triển tiếp theo kế hoạch Jira.

Backend hiện tại sử dụng Python Flask.
Mã Backend NestJS cũ được lưu trong lịch sử Git.
## Script hỗ trợ PostgreSQL trên Windows

File `scripts/run_postgres.sh` kiểm tra PostgreSQL, thử khởi động
service `postgresql-x64-16` khi cần và tạo database nếu chưa tồn tại.

Yêu cầu PostgreSQL 16 và Git Bash. Chạy tại thư mục `backend-python`:

```bash
bash scripts/run_postgres.sh arimms_python
```

Nếu dùng PowerShell, gọi Bash bằng đường dẫn cài Git trên máy.
Ví dụ:

```powershell
& "D:\cuocdoimoi\Git\bin\bash.exe" ./scripts/run_postgres.sh arimms_python
```

Tên database được truyền bằng tham số đầu tiên.
Script giữ nguyên database đã tồn tại và không tự chạy migration hoặc seed.

Nếu cần khởi động Windows Service, có thể phải chạy Terminal
với quyền Administrator.
