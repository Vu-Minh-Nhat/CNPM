# AR-IMMS — Web Management Portal

Web Portal sử dụng Next.js, React và TypeScript; kết nối tới Backend Flask.

## 1. Chức năng

- Đăng nhập và đăng xuất.
- Xem Dashboard và danh sách tài sản.
- Xem Node, Rack, Room, Site, Workload và telemetry.
- Xem, lọc và xác nhận cảnh báo theo quyền.
- Xem và cấu hình Alert Rule theo quyền.
- Tạo Ticket từ cảnh báo, phân công và xử lý Ticket theo vai trò.

Phân quyền thực tế luôn được kiểm tra ở backend; việc ẩn nút trên giao diện
không thay thế kiểm tra quyền API.

## 2. Chuẩn bị

- Cài Node.js và npm phù hợp với dự án.
- Backend đã cấu hình, migration, seed và đang chạy.
- Có tài khoản đăng nhập đã được seed.

Xem [README Backend](../backend-python/README.md).

## 3. Cài đặt

Tại thư mục gốc dự án:

```powershell
cd frontend
npm ci
```

## 4. Cấu hình Backend URL

Tạo file cá nhân:

```powershell
Copy-Item .env.example .env.local
notepad .env.local
```

Ví dụ backend chạy HTTP cổng 5002:

```env
NEXT_PUBLIC_API_URL=http://localhost:5002
```

Địa chỉ này phải khớp backend thực tế. Backend cần cho phép origin frontend,
ví dụ `http://localhost:3001`, trong `CORS_ORIGINS`.

Khởi động lại frontend sau khi thay `.env.local`.

## 5. Chạy Web Portal

```powershell
npm run dev -- --port 3001
```

Mở:

```text
http://localhost:3001
```

Giữ backend và frontend chạy trong hai terminal riêng.

## 6. Đường dẫn chính

| Đường dẫn | Nội dung |
| --- | --- |
| `/` | Đăng nhập |
| `/dashboard` | Dashboard |
| `/assets` | Tra cứu tài sản |
| `/alerts` | Danh sách cảnh báo |
| `/alerts/rules` | Cấu hình quy tắc cảnh báo |
| `/tickets` | Ticket bảo trì |
| `/users` | Quản lý tài khoản |
| `/forbidden` | Thông báo không đủ quyền |

Theo cấu hình hiện tại, Administrator và Operator được quản lý Alert Rule;
Technician chỉ xem. Quyền Ticket được kiểm tra theo vai trò ở backend.

## 7. Kiểm tra Alert và Ticket

1. Đăng nhập Operator.
2. Mở `/alerts`.
3. Chọn chi tiết một cảnh báo.
4. Nhấn **Tạo ticket từ cảnh báo**.
5. Kiểm tra Node và Alert được điền sẵn.
6. Nhập thông tin và tạo Ticket.
7. Kiểm tra Ticket và lịch sử thao tác.

Để có cảnh báo thật, cần Agent gửi telemetry mới, rule đang bật và Alert
Worker đang chạy. Không coi giao diện rỗng là lỗi nếu backend không có cảnh báo.

## 8. Lint và build

```powershell
npm run lint
npm run build
```

Chạy bản production build để kiểm tra cục bộ:

```powershell
npm run start -- --port 3001
```

Dừng dev server đang dùng cổng 3001 trước khi chạy lệnh này.

## 9. Xử lý lỗi

- **Không kết nối backend:** kiểm tra backend, `/health`, `NEXT_PUBLIC_API_URL`
  và CORS; sau khi đổi `.env.local`, khởi động lại frontend.
- **401:** kiểm tra phiên đăng nhập và đăng nhập lại.
- **403:** tài khoản không đủ quyền cho thao tác.
- **Không có cảnh báo:** kiểm tra Node, telemetry mới, rule đang bật và worker.
- **Cổng 3001 đã dùng:** dừng tiến trình cũ hoặc chọn cổng khác và cập nhật CORS.

Không commit `.env.local`, `node_modules/` hoặc `.next/`.
