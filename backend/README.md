## 1. Thiết lập Backend

Backend nằm trong thư mục `backend/`.

Xem [hướng dẫn Backend](backend/README.md).

### 2. Chuẩn bị

- Git.
- Node.js 24 LTS, từ 24.15 trở lên.
- npm.
- PostgreSQL 16.
- Database phát triển riêng của từng thành viên.

### 2.1. Tải mã nguồn và cài dependency

```powershell
git clone https://github.com/Vu-Minh-Nhat/CNPM.git
cd CNPM/backend
npm ci
```

Nếu đã clone repository, dùng bản hiện có và cập nhật
nhánh phù hợp thay vì clone lại.

### 2.2-. Cấu hình môi trường

Trong thư mục `backend`:

```powershell
Copy-Item .env.example .env
```

Nếu đã có `.env`, chỉnh file hiện có, không sao chép đè.

Ví dụ các giá trị cần cấu hình:

```dotenv
NODE_ENV=development
PORT=3000
CORS_ORIGINS=http://localhost:3001,http://localhost:5173
DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/DATABASE_NAME
JWT_SECRET=
SEED_PASSWORD=
```

- Thay USERNAME, PASSWORD và DATABASE_NAME bằng thông tin
  PostgreSQL trên máy.
- Mỗi thành viên sử dụng database phát triển riêng.
- Mật khẩu trong DATABASE_URL cần được mã hóa URL nếu chứa
  ký tự đặc biệt.
- JWT_SECRET là khóa ký token, khác mật khẩu PostgreSQL.
- SEED_PASSWORD là mật khẩu cho các tài khoản ứng dụng mẫu:
  ít nhất 12 ký tự và tối đa 72 byte UTF-8.
- Nếu Frontend sử dụng cổng khác, cập nhật CORS_ORIGINS.
- Không commit `.env` hoặc thông tin xác thực.

Tạo giá trị ngẫu nhiên rồi điền vào JWT_SECRET:

```powershell
node -e "console.log(require('node:crypto').randomBytes(32).toString('hex'))"
```

### 2.3. Khởi tạo database

Tạo database trống bằng pgAdmin hoặc psql trước khi chạy:

```powershell
npm run db:check
npm run build
npm run migration:run
npm run migration:status
npm run db:seed
```

Chỉ chạy lệnh tiếp theo khi lệnh trước thành công.

Migration tạo cấu trúc bảng. Seed tạo dữ liệu mẫu.
Ứng dụng không tự chạy migration khi khởi động.

Chạy lại seed không ghi đè dữ liệu đã tồn tại hoặc đặt lại
mật khẩu tài khoản mẫu.

### 2.4. Chạy ứng dụng

```powershell
npm run start:dev
```

Kiểm tra:

```text
GET http://localhost:3000/health
```

Thay cổng nếu PORT đã được cấu hình khác.

Endpoint `/health` xác nhận Backend đang chạy;
không thực hiện truy vấn kiểm tra database.

Chạy bản đã biên dịch:

```powershell
npm run build
npm run start:prod
```

## 3. Tài khoản mẫu

Sau khi chạy seed:

| Email | Vai trò |
|---|---|
| admin@arimms.local | Administrator |
| operator@arimms.local | Operator |
| tech@arimms.local | Technician |

Mật khẩu là giá trị SEED_PASSWORD được dùng khi các tài khoản
được tạo lần đầu.

Các tài khoản này chỉ phục vụ phát triển và kiểm thử.
Không đưa tài khoản mẫu vào môi trường production.

## 4. API hiện tại

| Phương thức | Endpoint | Mục đích | Quyền |
|---|---|---|---|
| GET | `/health` | Kiểm tra Backend đang chạy | Công khai |
| POST | `/auth/login` | Đăng nhập và nhận JWT | Công khai |
| GET | `/auth/me` | Xem thông tin người đăng nhập | Các vai trò |
| GET | `/users` | Xem danh sách tài khoản | Administrator |
| POST | `/users` | Tạo tài khoản | Administrator |
| PATCH | `/users/:id/role` | Thay đổi vai trò tài khoản | Administrator |
| GET | `/assets` | Đọc Node, Rack, Room, Site và Workload | Các vai trò |

Các API được bảo vệ yêu cầu header:

```text
Authorization: Bearer <access-token>
```

Các endpoint POST `/assets`, PUT `/assets/:id` và
DELETE `/assets/:id` chưa triển khai nghiệp vụ lưu trữ.

## 5. Kiểm thử

Trong thư mục `backend`, chạy:

```powershell
npm run build
npm test
npm run test:e2e
```

Kiểm thử e2e hiện sử dụng database phát triển đã migrate
và seed. Cấu hình DATABASE_URL và SEED_PASSWORD trong
`backend/.env` trước khi chạy.

SEED_PASSWORD phải trùng mật khẩu đã dùng khi tạo các tài khoản mẫu.

Các kiểm tra hiện có bao gồm:

- Đăng nhập thành công và sai mật khẩu.
- Token thiếu hoặc không hợp lệ.
- Quyền truy cập theo vai trò.
- Không trả password hash trong danh sách tài khoản.
- Truy vấn cây tài sản từ PostgreSQL.
- Endpoint health và cấu hình CORS.
- HTTP 501 cho chức năng ghi tài sản chưa triển khai.

Khóa ngoại, ràng buộc duy nhất, CHECK và khả năng chạy lại seed
đã được kiểm tra thủ công trong quá trình thực hiện AI-29.

## 6. Tài liệu

Tài liệu phân tích và hình minh họa nằm trong `docs/`.

Các nội dung tài liệu của dự án:

| Mã | Nội dung |
|---|---|
| AI-2 | Bối cảnh và vấn đề |
| AI-3 | Mục tiêu dự án |
| AI-4 | Phạm vi và giới hạn |
| AI-5 | Tác nhân hệ thống |
| AI-6 | Yêu cầu chức năng |
| AI-7 | Yêu cầu phi chức năng |
| AI-8 | Use Case |
| AI-9 | ERD |

## 7. Quy trình làm việc nhóm

1. Lưu công việc hiện tại bằng commit trên branch của mình.
2. Cập nhật `main`.
3. Tạo branch riêng cho task mới.
4. Phát triển và kiểm thử.
5. Commit, push và tạo Pull Request.
6. Review trước khi merge vào `main`.
7. Cập nhật minh chứng và trạng thái trên Jira.

Ví dụ bắt đầu task mới khi working tree đã sạch:

```powershell
git switch main
git pull origin main
git switch -c feature/AI-XX-task-name
```

Ví dụ push task:

```powershell
git add -A
git status
git commit -m "feat(AI-XX): describe the change"
git push -u origin feature/AI-XX-task-name
```

Kiểm tra danh sách file trước khi commit.
Không commit `.env`, mật khẩu, token, `node_modules` hoặc `dist`.

## 8. Giới hạn dự án

- Hệ thống được đánh giá trên Mini Data Center Testbed.
- Máy tính vật lý đại diện cho server; container đại diện cho workload.
- Mobile AR hướng tới Android.
- Dữ liệu mô phỏng phải được ghi rõ.
- Khả năng thu thập metric phụ thuộc thiết bị và quyền truy cập.
- Phân tích điện năng/PUE cần dữ liệu phù hợp về nguồn,
  đơn vị, phạm vi và thời gian đo.
- Không bao gồm tự động sửa chữa phần cứng.

## 9. Quản lý công việc

[Jira — AR-IMMS](https://phamvanut12121958.atlassian.net/jira/software/projects/AI/boards/2/backlog)