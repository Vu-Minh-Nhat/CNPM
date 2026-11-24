# AR-IMMS – Automated Remote Infrastructure Monitoring and Management System

AR-IMMS là hệ thống giám sát và quản lý hạ tầng CNTT. Hệ thống hỗ trợ quản lý tài sản, thu thập telemetry, theo dõi trạng thái thiết bị, quản lý cảnh báo và phân quyền người dùng.

## 1. Kiến trúc hệ thống

Dự án gồm các thành phần chính:

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| Frontend | Next.js, React, TypeScript | Giao diện quản trị và giám sát |
| Backend | Python, Flask | REST API, xác thực, nghiệp vụ và xử lý dữ liệu |
| Database | PostgreSQL | Lưu trữ người dùng, tài sản, telemetry và dữ liệu hệ thống |
| Collector Agent | Python, psutil, requests | Thu thập CPU, RAM, Disk và gửi telemetry |
| Secure communication | HTTPS, TLS, mTLS | Bảo vệ kết nối giữa Agent và Backend |

## 2. Yêu cầu môi trường

Cài đặt các phần mềm sau trước khi chạy dự án:

- Git
- Python và pip
- Node.js và npm
- PostgreSQL
- Visual Studio Code hoặc trình soạn thảo tương đương

Phiên bản đã được kiểm tra trong môi trường phát triển:

- Python 3.14.0
- Node.js 24.22.1
- npm 11.19.1

Lưu ý: Cần kiểm tra khả năng tương thích của các thư viện Python trong `requirements.txt` nếu sử dụng phiên bản Python khác.

## 3. Clone source code

```powershell
git clone https://github.com/Vu-Minh-Nhat/CNPM.git
cd CNPM
```

Cấu trúc thư mục chính:

```text
CNPM/
├── frontend/
├── backend-python/
├── agent/
├── docs/
└── README.md
```

## 4. Cấu hình PostgreSQL

1. Khởi động PostgreSQL.
2. Tạo database cho dự án, ví dụ `arimms_python`.
3. Chuẩn bị tài khoản PostgreSQL có quyền truy cập database.
4. Cấu hình chuỗi kết nối trong file môi trường Backend.

Ví dụ:

```env
DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/arimms_python
```

Thay `USERNAME` và `PASSWORD` bằng thông tin PostgreSQL trên máy đang chạy.

Không sử dụng mật khẩu mẫu trong môi trường triển khai thực tế.

## 5. Cài đặt và chạy Backend

### 5.1. Tạo môi trường Python

Mở PowerShell tại thư mục gốc dự án:

```powershell
cd backend-python

py -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt
```

Nếu PowerShell chặn việc kích hoạt môi trường ảo, có thể cho phép script trong phiên hiện tại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Sau đó kích hoạt lại:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5.2. Cấu hình môi trường

Tạo file `.env.migration` từ file mẫu:

```powershell
Copy-Item .env.example .env.migration
```

Mở `.env.migration` và cấu hình:

```env
DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/arimms_python

JWT_SECRET=YOUR_GENERATED_SECRET
JWT_EXPIRES_IN_SECONDS=86400

CORS_ORIGINS=http://localhost:3001

TELEMETRY_AGENT_KEY=
TELEMETRY_AGENT_NODE_IDS=

TELEMETRY_STALE_AFTER_SECONDS=30
TELEMETRY_OFFLINE_AFTER_SECONDS=90
TELEMETRY_POLL_INTERVAL_SECONDS=5
```

Có thể tạo JWT secret bằng:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Sao chép giá trị được tạo vào `JWT_SECRET`.

### 5.3. Khởi tạo database

Sau khi cấu hình kết nối PostgreSQL, chạy migration:

```powershell
python -m alembic upgrade head
```

Nếu lệnh migration báo lỗi, kiểm tra lại `DATABASE_URL`, trạng thái PostgreSQL và cấu hình Alembic trước khi tiếp tục.

### 5.4. Chạy Backend

Trong thư mục `backend-python`:

```powershell
.\run.bat
```

Theo cấu hình runner hiện tại, Backend chạy tại:

- API: `http://127.0.0.1:5002`
- Health check: `http://127.0.0.1:5002/health`
- Swagger UI: `http://127.0.0.1:5002/docs/`

Giữ cửa sổ terminal này hoạt động trong suốt quá trình sử dụng.

## 6. Cài đặt và chạy Frontend

Mở một cửa sổ PowerShell mới:

```powershell
cd CNPM\frontend
```

Nếu đã ở trong thư mục gốc repository thì chỉ cần:

```powershell
cd frontend
```

### 6.1. Cài đặt dependencies

```powershell
npm ci
```

### 6.2. Cấu hình API

Tạo file `.env.local`:

```powershell
Copy-Item .env.example .env.local
```

Cấu hình URL Backend trong `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:5002
```

URL này tương ứng với Backend chạy bằng `run.bat` ở cổng 5002.

Đảm bảo Backend có cấu hình CORS:

```env
CORS_ORIGINS=http://localhost:3001
```

### 6.3. Chạy Frontend

```powershell
npm run dev -- --port 3001
```

Truy cập:

**http://localhost:3001**

### 6.4. Kiểm tra và build Frontend

Kiểm tra lint:

```powershell
npm run lint
```

Build production:

```powershell
npm run build
```

Chạy production server:

```powershell
npm run start -- --port 3001
```

## 7. Cài đặt Collector Agent

Collector Agent thu thập thông tin tài nguyên hệ thống:

- CPU usage
- RAM usage
- Disk usage

Agent gửi dữ liệu telemetry đến Backend theo chu kỳ cấu hình.

### 7.1. Tạo môi trường Python

Mở PowerShell mới:

```powershell
cd agent

py -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt
```

### 7.2. Cấu hình Agent

Tạo file `.env` từ file mẫu:

```powershell
Copy-Item .env.example .env
```

Cấu hình cơ bản:

```env
BACKEND_URL=https://localhost:5002
TELEMETRY_ENDPOINT=/telemetry

NODE_ID=YOUR_NODE_ID

SEND_INTERVAL_SECONDS=5
REQUEST_TIMEOUT_SECONDS=5
MAX_RETRIES=3
RETRY_DELAY_SECONDS=2
```

Agent hiện sử dụng HTTPS và yêu cầu mutual TLS. Các đường dẫn mặc định trong `agent/config.py` là:

```text
agent/certs-v2/agent.crt
agent/certs-v2/agent.key
agent/certs-v2/ca.crt
```

Cần có đủ ba file chứng chỉ tương ứng trước khi chạy Agent.

### 7.3. Chạy Agent

Sau khi cấu hình đầy đủ URL, Node ID và chứng chỉ:

```powershell
.\run.bat
```

Theo dõi log để kiểm tra trạng thái thu thập và gửi telemetry.

**Lưu ý về mTLS:** Không sử dụng `http://localhost:5002` cho Agent. Backend mTLS phải được chạy bằng TLS runner và phải có server certificate, server private key cùng CA certificate hợp lệ. Backend mTLS hiện sử dụng `ssl.CERT_REQUIRED`, do đó Agent phải trình client certificate được CA tin cậy ký.

Script tạo chứng chỉ hiện có sự khác biệt về thư mục đầu ra so với các đường dẫn `certs-v2` đang được cấu hình. Cần thống nhất hai đường dẫn này trước khi dùng script tạo chứng chỉ. Không ghi đè các chứng chỉ hiện có.

Quy trình đăng ký Agent và cấp quyền Node cần được hoàn thiện/xác minh trước khi triển khai thực tế.

## 8. Thứ tự khởi động hệ thống

Khi chạy toàn bộ hệ thống trong môi trường phát triển:

1. Khởi động PostgreSQL.
2. Khởi động Backend.
3. Khởi động Frontend.
4. Cấu hình và khởi động Collector Agent sau khi Backend mTLS và chứng chỉ đã sẵn sàng.

Mỗi thành phần nên chạy trong một cửa sổ terminal riêng để thuận tiện theo dõi log và xử lý lỗi.

## 9. Kiểm tra hoạt động

### Backend

Mở:

```text
http://127.0.0.1:5002/health
```

Kiểm tra Swagger:

```text
http://127.0.0.1:5002/docs/
```

### Frontend

Mở:

```text
http://localhost:3001
```

Kiểm tra đăng nhập, điều hướng và các chức năng được cấp quyền.

### Agent

Kiểm tra log để xác nhận:

- Agent khởi động thành công.
- Cấu hình Node ID hợp lệ.
- Các file chứng chỉ tồn tại.
- Thu thập được CPU, RAM và Disk.
- Kết nối HTTPS thành công.
- Backend chấp nhận telemetry.

## 10. Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân có thể | Cách kiểm tra |
|---|---|---|
| `DATABASE_URL is not configured` | Thiếu cấu hình database | Kiểm tra file `.env` và `.env.migration` |
| PostgreSQL connection refused | PostgreSQL chưa chạy hoặc sai cổng | Kiểm tra service và cổng PostgreSQL |
| Frontend không kết nối được API | Sai `NEXT_PUBLIC_API_URL` hoặc Backend chưa chạy | Kiểm tra URL và cổng Backend |
| CORS error | Origin Frontend chưa được cho phép | Kiểm tra `CORS_ORIGINS` |
| `EADDRINUSE` | Cổng đang được tiến trình khác sử dụng | Kiểm tra tiến trình chiếm cổng |
| `WRONG_VERSION_NUMBER` | Gửi HTTPS đến server HTTP hoặc ngược lại | Kiểm tra giao thức của Backend |
| `CERTIFICATE_VERIFY_FAILED` | CA hoặc server certificate không hợp lệ | Kiểm tra CA và chứng chỉ |
| Client certificate required | Agent chưa gửi client certificate hợp lệ | Kiểm tra `agent.crt`, `agent.key` và CA |
| Agent báo thiếu `NODE_ID` | Chưa cấu hình Node ID | Kiểm tra file `.env` của Agent |

## 11. Bảo mật và lưu ý Git

Không commit các thông tin nhạy cảm sau:

- File `.env`, `.env.local`, `.env.migration`.
- Database password.
- JWT secret và API key.
- Private key (`*.key`).
- Certificate và thư mục chứng chỉ phát triển.
- File backup database.

Các file môi trường mẫu `.env.example` có thể được commit nếu không chứa thông tin bí mật.

Trước khi push code lên GitHub, kiểm tra:

```powershell
git status --short
git diff --check
```

Không sử dụng `git add .` nếu repository đang có những thay đổi không thuộc phạm vi công việc cần commit.

## 12. Repository

GitHub: https://github.com/Vu-Minh-Nhat/CNPM
