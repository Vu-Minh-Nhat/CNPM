# AR-IMMS — Web Management Portal

Web Portal của AR-IMMS được phát triển bằng Next.js, React và TypeScript,
kết nối với Backend Python Flask.

## 1. Chức năng hiện có

- Đăng nhập bằng tài khoản hệ thống.
- Xác minh phiên đăng nhập qua JWT.
- Header hiển thị email, vai trò và nút đăng xuất.
- Sidebar và điều hướng theo vai trò.
- Trang Dashboard.
- Danh sách tài sản Node/Server.
- Tìm kiếm theo mã, tên, serial hoặc vị trí.
- Lọc tài sản theo Site và xóa bộ lọc.
- Xem chi tiết Node cùng Rack, Room, Site và Workload.
- Trang không có quyền và trang không tìm thấy.

Mức độ hoàn thiện Dashboard và quản trị tài khoản được cập nhật
theo các task tương ứng trên Jira.

## 2. Yêu cầu môi trường

- Node.js và npm tương thích với phiên bản Next.js trong package.json.
- Backend Flask đã được cấu hình và khởi động.
- PostgreSQL đã có dữ liệu phù hợp để kiểm tra.
- Có tài khoản đăng nhập hợp lệ.

Xem [hướng dẫn Backend Python](../backend-python/README.md)
để cài đặt Backend, chạy migration và seed.

## 3. Cài đặt

Tại thư mục gốc repository:

```powershell
cd frontend
npm ci
```

Lệnh `npm ci` cài dependencies theo `package-lock.json`.

## 4. Cấu hình môi trường

Nếu chưa có file `.env.local`, tạo từ mẫu:

```powershell
Copy-Item .env.example .env.local
```

Cấu hình địa chỉ Backend:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:5000
```

Nếu Backend đang chạy ở cổng khác, thay bằng địa chỉ thực tế.
Ví dụ khi kiểm tra Backend tại cổng 5002:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:5002
```

Sau khi thay đổi cấu hình, khởi động lại Frontend.
Nếu chạy bản đã build, cần build lại với cấu hình mới.

Biến `NEXT_PUBLIC_API_URL` có thể xuất hiện trong mã trình duyệt.
Không đưa mật khẩu database hoặc khóa JWT vào biến này.

Backend cần cho phép origin Frontend, ví dụ:

```dotenv
CORS_ORIGINS=http://localhost:3001
```

Biến `CORS_ORIGINS` được cấu hình ở Backend.

## 5. Chạy khi phát triển

Tại thư mục `frontend`:

```powershell
npm run dev -- --port 3001
```

Mở:

```text
http://localhost:3001
```

Giữ Backend và Frontend chạy trong hai Terminal riêng.

Địa chỉ Backend mặc định:

| Thành phần | Địa chỉ |
| --- | --- |
| Backend Flask | http://localhost:5000 |
| Kiểm tra hoạt động | http://localhost:5000/health |
| Swagger UI | http://localhost:5000/docs/ |
| OpenAPI JSON | http://localhost:5000/openapi.json |

## 6. Tài khoản mẫu

Khi Backend đã seed thành công:

| Email | Vai trò |
| --- | --- |
| admin@arimms.local | Administrator |
| operator@arimms.local | Operator |
| tech@arimms.local | Technician |

Dùng mật khẩu đã đặt khi seed database mà Backend đang kết nối.
Không có mật khẩu cố định chung cho mọi môi trường.

Chạy lại seed không tự thay đổi mật khẩu tài khoản đã tồn tại.

## 7. Cấu trúc mã nguồn

```text
src/
├── app/
│   ├── (portal)/
│   │   ├── assets/page.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── forbidden/page.tsx
│   │   ├── users/page.tsx
│   │   └── layout.tsx
│   ├── globals.css
│   ├── layout.tsx
│   ├── not-found.tsx
│   └── page.tsx
├── components/
│   ├── assets/
│   └── layout/
├── contexts/
├── lib/
│   ├── api-client.ts
│   ├── assets.ts
│   ├── auth-storage.ts
│   └── auth.ts
└── types/
```

- `app/`: các trang và layout theo Next.js App Router.
- `components/`: thành phần giao diện dùng chung.
- `contexts/`: trạng thái dùng chung của ứng dụng.
- `lib/`: quản lý phiên, gọi API và các hàm hỗ trợ.
- `types/`: kiểu dữ liệu dùng chung.

Nhóm `(portal)` tổ chức layout, không xuất hiện trong URL.

## 8. Điều hướng và phân quyền

| Đường dẫn | Quyền truy cập giao diện |
| --- | --- |
| `/` | Trang đăng nhập |
| `/dashboard` | Administrator, Operator, Technician |
| `/assets` | Administrator, Operator, Technician |
| `/users` | Administrator |
| `/forbidden` | Trang thông báo không có quyền |

- Administrator thấy menu Quản lý tài khoản.
- Operator và Technician không thấy menu Quản lý tài khoản.
- Người dùng chưa đăng nhập cần đăng nhập trước khi vào Portal.
- Header hiển thị thông tin tài khoản được xác minh qua `/auth/me`.
- Đăng xuất xóa thông tin phiên ở trình duyệt.

Ẩn menu trên Frontend không thay thế kiểm tra quyền ở Backend.
Các API vẫn phải xác thực JWT và kiểm tra RBAC.

## 9. Trang tài sản — AI-41

Trang `/assets` sử dụng:

```http
GET /assets
Authorization: Bearer <accessToken>
```

Chức năng:

- Hiển thị mã Node, tên, serial và vị trí.
- Tìm kiếm trên dữ liệu đã tải.
- Lọc theo Site.
- Xóa từ khóa và bộ lọc.
- Mở, đóng khung chi tiết.
- Hiển thị quan hệ Rack → Room → Site và danh sách Workload.
- Xử lý trạng thái đang tải, lỗi, dữ liệu thiếu và kết quả rỗng.

Chi tiết được lấy từ danh sách đã tải.
Không gọi endpoint chi tiết `/assets/{id}`.

Phạm vi AI-41 không bao gồm tạo, sửa hoặc xóa tài sản.

Dữ liệu mẫu để kiểm tra:

```text
DEMO-SITE
└── ROOM-01
    └── RACK-01
        └── DEMO-NODE-01
            └── DEMO-WORKLOAD-01
```

## 10. Kiểm tra và build

Tại thư mục `frontend`:

```powershell
npm run lint
npm run build
```

Chạy bản sau khi build:

```powershell
npm run start -- --port 3001
```

Dừng Frontend phát triển đang dùng cổng 3001 trước khi chạy bản này.

## 11. Kiểm tra tích hợp

Thực hiện sau khi cấu hình Backend và Frontend:

- Đăng nhập bằng tài khoản hợp lệ.
- Kiểm tra email và vai trò trên Header.
- Kiểm tra menu theo vai trò.
- Mở Dashboard và Tài sản.
- Tìm kiếm DEMO-NODE-01.
- Tìm kiếm mã không tồn tại và kiểm tra thông báo rỗng.
- Chọn Site và xóa bộ lọc.
- Mở chi tiết, kiểm tra Rack, Room, Site và Workload.
- Đóng khung chi tiết.
- Đăng xuất và kiểm tra trang được bảo vệ.
- Kiểm tra trang không có quyền và trang 404.

Chỉ ghi nhận PASS cho những trường hợp đã chạy thực tế.

## 12. Xử lý lỗi thường gặp

### Không kết nối được Backend

- Kiểm tra Backend đang chạy.
- Kiểm tra `NEXT_PUBLIC_API_URL`.
- Mở `/health` của Backend để xác nhận có phản hồi.
- Kiểm tra CORS cho đúng origin Frontend.
- Khởi động lại Frontend sau khi sửa `.env.local`.

### Đăng nhập trả về 401

- Kiểm tra email và mật khẩu Web AR-IMMS.
- Kiểm tra Backend đang kết nối database nào.
- Mật khẩu Web khác mật khẩu PostgreSQL.
- Nếu phiên hết hạn, đăng nhập lại.

### API trả về 403

Tài khoản đã được xác thực nhưng không đủ quyền.
Kiểm tra vai trò và quyền của endpoint tương ứng.

### Cổng 3001 đang được sử dụng

Dừng tiến trình Frontend cũ hoặc chọn cổng khác.
Nếu đổi cổng Frontend, cập nhật CORS ở Backend cho phù hợp.

## 13. Quy ước làm việc

- Component dùng tên PascalCase.
- File component ưu tiên kebab-case.
- Trang và layout tuân theo quy ước Next.js.
- Các trang Portal dùng layout chung.
- Địa chỉ Backend lấy từ biến môi trường.
- Cập nhật tài liệu khi thay đổi API hoặc cấu hình.
- Commit `package.json`, `package-lock.json` và `.env.example`.
- Không commit `.env.local`, `node_modules/`, `.next/`
  hoặc thông tin bí mật.

## 14. Phạm vi phát triển tiếp

Các màn hình telemetry, cảnh báo, lịch sử, ticket,
audit và báo cáo được phát triển theo kế hoạch Jira.

Việc chạy được giao diện cục bộ chưa xác nhận hệ thống đã
được triển khai production.