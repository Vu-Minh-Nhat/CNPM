# AR-IMMS

**AR-Integrated Infrastructure Monitoring and Maintenance System**

Hệ thống giám sát và bảo trì hạ tầng tích hợp thực tế tăng cường,
được phát triển và đánh giá trên Mini Data Center Testbed.

## 1. Giới thiệu

AR-IMMS liên kết thiết bị vật lý với dữ liệu giám sát,
cảnh báo và lịch sử bảo trì.

Web Portal hỗ trợ quản lý tập trung. Ứng dụng Mobile AR
hỗ trợ kỹ thuật viên nhận diện và tra cứu thông tin thiết bị
tại hiện trường.

## 2. Người sử dụng

| Vai trò | Trách nhiệm chính |
|---|---|
| System Administrator | Quản lý tài khoản, phân quyền, cấu hình, sức khỏe hệ thống và audit log |
| System Operator | Quản lý tài sản, giám sát telemetry, xử lý cảnh báo, phân công và phê duyệt đóng ticket |
| Technician | Nhận công việc, quét marker AR, kiểm tra thiết bị và cập nhật kết quả bảo trì |

Collector Agent là thành phần phần mềm thu thập và gửi telemetry
từ môi trường thử nghiệm về Backend.

## 3. Các chức năng dự kiến

- Xác thực người dùng và phân quyền RBAC.
- Quản lý cấu trúc Site → Room → Rack → Node/Server → Workload.
- Nhận diện thiết bị thông qua marker QR/ArUco.
- Giám sát telemetry và trạng thái kết nối.
- Hiển thị dữ liệu thời gian thực trên Web và Mobile.
- Phát hiện và quản lý cảnh báo.
- Quản lý ticket sự cố và bảo trì.
- Tra cứu lịch sử telemetry, bảo trì và audit.
- Báo cáo vận hành và phân tích năng lượng khi có dữ liệu phù hợp.

Danh sách trên mô tả phạm vi sản phẩm.
Trạng thái triển khai hiện tại được trình bày ở mục 6.

## 4. Cấu trúc repository

```text
CNPM/
├── docs/              # SRS, sơ đồ và báo cáo
├── backend/           # NestJS Backend
├── frontend/          # Web Portal Next.js
├── mobile/            # Ứng dụng Mobile AR
├── agent/             # Collector Agent
├── skills/            # Hướng dẫn và quy trình làm việc dùng lại
├── README.md          # Giới thiệu toàn dự án
├── checklist.md       # Theo dõi công việc, bổ sung theo tiến độ
└── .gitignore
```

Backend nằm trong thư mục `backend/`.
Xem [hướng dẫn Backend](backend/README.md).

Các thành phần chưa triển khai có thể chỉ chứa README mô tả kế hoạch.
Git không lưu thư mục rỗng.

## 5. Công nghệ

| Thành phần | Công nghệ |
|---|---|
| Backend | NestJS, TypeScript |
| ORM | TypeORM |
| Database | PostgreSQL |
| Xác thực | JWT |
| Phân quyền | RBAC |
| Web Portal — dự kiến | Next.js |
| Mobile AR — dự kiến | React Native trên Android |
| Truyền dữ liệu thời gian thực — dự kiến | Socket.IO |
| Workload thử nghiệm — dự kiến | Docker |
| Kết nối Agent — dự kiến | mTLS |
| Quản lý mã nguồn | Git, GitHub |
| Quản lý công việc | Jira |

Phiên bản dependency cụ thể được khai báo trong
`package.json` và `package-lock.json` của từng thành phần.

## 6. Trạng thái triển khai Backend

### Đã triển khai và kiểm tra trong môi trường phát triển

- Khởi tạo NestJS và TypeScript.
- Cấu hình biến môi trường, PORT và CORS.
- Endpoint kiểm tra hoạt động `/health`.
- Kết nối PostgreSQL thông qua `DATABASE_URL`.
- Tích hợp TypeORM và migration.
- Tạo bảng vai trò, người dùng và cây tài sản.
- Thiết lập khóa ngoại, khóa duy nhất và ràng buộc dữ liệu.
- Tạo dữ liệu mẫu; chạy lại seed không tạo bản ghi trùng.
- Đăng nhập bằng tài khoản lưu trong PostgreSQL.
- Đọc danh sách tài khoản theo quyền Administrator.
- Đọc Node cùng Rack, Room, Site và Workload.
- Kiểm thử Backend gồm xác thực, phân quyền, truy vấn tài sản,
  health và CORS.

### Chưa triển khai hoặc chưa xác nhận hoàn thành

- Tạo, sửa và xóa tài sản qua API.
- Collector Agent và tiếp nhận telemetry.
- Socket.IO và dashboard thời gian thực.
- Cảnh báo và quy trình ticket.
- Mobile AR.
- Báo cáo năng lượng và audit đầy đủ.
- Triển khai và đánh giá toàn hệ thống.

CRUD hạ tầng đã được triển khai qua `/sites`, `/rooms`,
`/racks` và `/servers`. Các endpoint ghi `/assets`
tổng quát vẫn trả HTTP 501.
khi người gọi có quyền truy cập.

## 7. Khởi chạy Backend

### 7.1. Yêu cầu

- Git.
- Node.js 24 LTS, từ 24.15 trở lên.
- npm.
- PostgreSQL 16.
- Một database phát triển riêng cho mỗi thành viên.

### 7.2. Tải mã nguồn

```powershell
git clone https://github.com/Vu-Minh-Nhat/CNPM.git
cd CNPM/backend
npm ci
```

### 7.3. Cấu hình môi trường

Trong PowerShell:

```powershell
Copy-Item .env.example .env
```

Nếu đã có `.env`, chỉnh file hiện có, không sao chép đè.

Điền cấu hình tương ứng với máy cá nhân:

```dotenv
NODE_ENV=development
PORT=3000
CORS_ORIGINS=http://localhost:3001,http://localhost:5173

DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/DATABASE_NAME

JWT_SECRET=
SEED_PASSWORD=
```

- Thay `USERNAME`, `PASSWORD` và `DATABASE_NAME` bằng thông tin thực tế.
- Mật khẩu trong `DATABASE_URL` phải được mã hóa URL nếu chứa ký tự đặc biệt.
- Tạo khóa JWT riêng và điền vào `JWT_SECRET`.
- Đặt `SEED_PASSWORD` ít nhất 12 ký tự và tối đa 72 byte.
- Nếu Web dùng cổng 3000, đổi cổng Web hoặc Backend và cập nhật CORS.
- Không đưa file `.env` hoặc mật khẩu thật lên GitHub.

Có thể tạo khóa JWT bằng:

```powershell
node -e "console.log(require('node:crypto').randomBytes(32).toString('hex'))"
```

### 7.4. Khởi tạo database

Tạo database phát triển trống bằng pgAdmin hoặc công cụ PostgreSQL,
sau đó chạy lần lượt:

```powershell
npm run db:check
npm run build
npm run migration:run
npm run migration:status
npm run db:seed
```

Chỉ chạy bước tiếp theo khi bước trước thành công.

Migration tạo các bảng:

| Bảng | Mục đích |
|---|---|
| roles | Vai trò người dùng |
| users | Tài khoản |
| sites | Địa điểm |
| rooms | Phòng thuộc Site |
| racks | Rack thuộc Room |
| nodes | Node/Server thuộc Rack |
| workloads | Workload thuộc Node |
| schema_migrations | Theo dõi migration đã áp dụng |

Các bảng nghiệp vụ khác được bổ sung bằng migration
theo tiến độ phát triển.

Schema không tự đồng bộ khi Backend khởi động.
Thay đổi cấu trúc database phải được quản lý bằng migration.

### 7.5. Dữ liệu mẫu

| Email | Vai trò |
|---|---|
| admin@arimms.local | Administrator |
| operator@arimms.local | Operator |
| tech@arimms.local | Technician |

Ba tài khoản sử dụng mật khẩu đã đặt trong `SEED_PASSWORD`
tại thời điểm tạo dữ liệu mẫu.

Seed cũng tạo cây tài sản:

```text
DEMO-SITE
└── ROOM-01
    └── RACK-01
        └── DEMO-NODE-01
            └── DEMO-WORKLOAD-01
```

Dữ liệu này phục vụ phát triển và kiểm thử.

Chạy lại seed giữ nguyên dữ liệu đã tồn tại.
Đổi `SEED_PASSWORD` không tự thay đổi mật khẩu tài khoản đã tạo.

### 7.6. Chạy ứng dụng

```powershell
npm run start:dev
```

Theo cấu hình mặc định, Backend chạy tại:

```text
http://localhost:3000
```

Kiểm tra:

```text
GET http://localhost:3000/health
```

Endpoint `/health` xác nhận Backend đang chạy,
không thực hiện truy vấn kiểm tra database trong mỗi request.

Chạy bản đã biên dịch:

```powershell
npm run build
npm run start:prod
```

## 8. API hiện có

| Phương thức | Endpoint | Quyền | Nội dung |
|---|---|---|---|
| GET | `/health` | Công khai | Kiểm tra hoạt động Backend |
| POST | `/auth/login` | Công khai | Đăng nhập |
| GET | `/auth/me` | Mọi vai trò đã đăng nhập | Xem tài khoản đang đăng nhập |
| GET | `/users` | Administrator | Danh sách tài khoản |
| POST | `/users` | Administrator | Tạo tài khoản |
| PATCH | `/users/:id/role` | Administrator | Thay đổi vai trò |
| GET | `/assets` | Mọi vai trò đã đăng nhập | Đọc Node và các quan hệ tài sản |

Các endpoint được bảo vệ yêu cầu header:

```text
Authorization: Bearer <access-token>
```

Các endpoint tài sản chưa triển khai:

| Phương thức | Endpoint | Vai trò được phép gọi | Kết quả hiện tại |
|---|---|---|---|
| POST | `/assets` | Administrator, Operator | HTTP 501 |
| PUT | `/assets/:id` | Administrator, Operator | HTTP 501 |
| DELETE | `/assets/:id` | Administrator | HTTP 501 |

Người dùng không có quyền sẽ nhận HTTP 403;
request thiếu token hoặc token không hợp lệ sẽ nhận HTTP 401.

## 9. Kiểm thử

Chạy trong thư mục `backend/`:

```powershell
npm run build
npm test
npm run test:e2e
```

Kiểm thử e2e cần database phát triển đã migrate và seed.
`SEED_PASSWORD` phải trùng mật khẩu của các tài khoản mẫu đã tạo.

Các nhóm kiểm tra hiện có:

- Đăng nhập và từ chối mật khẩu sai.
- Từ chối request thiếu token hoặc token không hợp lệ.
- Phân quyền truy cập tài khoản và tài sản.
- Không trả password hash trong danh sách tài khoản.
- Truy vấn quan hệ Node → Rack → Room → Site và Workload.
- Endpoint health và CORS.

Khóa ngoại, khóa duy nhất và ràng buộc sức chứa Rack
đã được kiểm tra thủ công trong database phát triển.

## 10. Tài liệu

Tài liệu phân tích được lưu trong [`docs/srs/`](docs/srs/).

Nội dung phân tích gồm:

- Bối cảnh và vấn đề.
- Mục tiêu dự án.
- Phạm vi và giới hạn.
- Tác nhân hệ thống.
- Yêu cầu chức năng.
- Yêu cầu phi chức năng.
- Use Case.
- ERD.

Sơ đồ, báo cáo sprint và hướng dẫn được bổ sung theo tiến độ.

## 11. Quy trình làm việc nhóm

Mỗi thành viên sử dụng database phát triển riêng,
tạo branch theo task và gửi Pull Request vào `main`.

Trước khi nhận task mới, lưu công việc đang làm,
sau đó cập nhật nhánh chung:

```powershell
git switch main
git pull origin main
git switch -c feature/AI-XX-task-name
```

Sau khi hoàn thành:

1. Build và chạy kiểm thử phù hợp.
2. Cập nhật tài liệu và `.env.example` nếu có cấu hình mới.
3. Kiểm tra danh sách file thay đổi.
4. Commit và push branch.
5. Tạo Pull Request, liên kết task Jira và kết quả kiểm thử.
6. Review trước khi merge vào `main`.

Không commit:

- `node_modules/`
- `dist/`
- `.env`
- Mật khẩu, token và khóa bí mật

Commit `package.json`, `package-lock.json`,
migration và cấu hình mẫu cần thiết để tái tạo môi trường.

## 12. Giới hạn dự án

- Đánh giá trên Mini Data Center Testbed.
- Chưa xác nhận khả năng vận hành trong Data Center thực tế.
- Khả năng thu thập metric phụ thuộc thiết bị và quyền truy cập.
- Mobile AR định hướng Android