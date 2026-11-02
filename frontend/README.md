# AR-IMMS Web Portal

Frontend của hệ thống AR-IMMS, sử dụng Next.js, React và TypeScript.

## 1. Yêu cầu

- Node.js và npm tương thích với phiên bản Next.js trong package.json.
- Backend được cấu hình và chạy theo hướng dẫn trong ../backend/README.md.
- Có tài khoản hợp lệ trong database để kiểm tra đăng nhập.

## 2. Cài đặt

Từ thư mục gốc repository:

```powershell
cd frontend
npm ci
```

## 3. Cấu hình môi trường

Sao chép cấu hình mẫu:

```powershell
Copy-Item .env.example .env.local
```

Nếu đã có .env.local, kiểm tra nội dung trước khi ghi đè.

Cấu hình địa chỉ Backend:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:3000
```

Biến NEXT_PUBLIC_API_URL được sử dụng trong trình duyệt,
không được chứa mật khẩu hoặc thông tin bí mật.

Khởi động lại Frontend sau khi thay đổi cấu hình môi trường.

Backend phải cho phép CORS từ địa chỉ Frontend,
mặc định khi phát triển là http://localhost:3001.

## 4. Chạy khi phát triển

```powershell
npm run dev -- --port 3001
```

Mở http://localhost:3001.

Backend mặc định chạy tại http://localhost:3000.

## 5. Kiểm tra và build

```powershell
npm run lint
npm run build
```

Chạy bản production sau khi build:

```powershell
npm run start -- --port 3001
```

Dừng server phát triển đang dùng cổng 3001 trước khi chạy bản production.

## 6. Cấu trúc mã nguồn

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
│   └── layout/
│       ├── header.tsx
│       └── sidebar.tsx
└── lib/
    └── auth.ts
```

- app: trang và layout theo App Router.
- components: component giao diện dùng chung.
- lib: các hàm hỗ trợ và gọi API; hiện có auth.ts.
- Kiểu dữ liệu dùng riêng được khai báo gần nơi sử dụng.
- Khi có kiểu dữ liệu dùng chung, đặt trong src/types/.

## 7. Quy ước

- File component sử dụng tên kebab-case, ví dụ sidebar.tsx.
- Tên component sử dụng PascalCase, ví dụ Sidebar.
- Tên trang và layout tuân theo quy ước của Next.js.
- Các trang Portal sử dụng layout chung trong app/(portal)/layout.tsx.
- Địa chỉ Backend lấy từ biến môi trường.
- Không commit .env.local, node_modules hoặc .next.

## 8. Điều hướng và phân quyền giao diện

| Đường dẫn | Quyền truy cập giao diện |
|---|---|
| / | Trang đăng nhập |
| /dashboard | Administrator, Operator, Technician |
| /assets | Administrator, Operator, Technician |
| /users | Administrator |
| /forbidden | Thông báo không có quyền cho người đã đăng nhập |

Header hiển thị email, vai trò và nút đăng xuất.

Sidebar đánh dấu menu đang chọn.
Menu Quản lý tài khoản chỉ hiển thị cho Administrator.

Thông tin tài khoản được xác minh qua GET /auth/me.
API nghiệp vụ vẫn phải kiểm tra JWT và RBAC tại Backend.

## 9. Phạm vi triển khai

Đã có khung giao diện, điều hướng và kết nối xác thực.

Dashboard, Tài sản và Quản lý tài khoản hiện là các trang khung.
Bảng dữ liệu và thao tác nghiệp vụ được triển khai trong task tương ứng.

Phiên đăng nhập hiện được lưu trong sessionStorage.
Đăng xuất xóa thông tin phiên ở trình duyệt và chuyển về trang đăng nhập.

## 10. Checklist kiểm tra thủ công

- [ ] Đăng nhập thành công với tài khoản hợp lệ.
- [ ] Header hiển thị đúng email và vai trò.
- [ ] Điều hướng Dashboard và Tài sản hoạt động.
- [ ] Menu đang chọn được đánh dấu.
- [ ] Administrator truy cập được Quản lý tài khoản.
- [ ] Operator và Technician không thấy menu Quản lý tài khoản.
- [ ] Operator và Technician nhập /users được chuyển sang /forbidden.
- [ ] Truy cập /dashboard khi chưa đăng nhập được chuyển về /.
- [ ] Đăng xuất rồi truy cập lại trang được bảo vệ phải đăng nhập.
- [ ] Đường dẫn không tồn tại hiển thị trang 404.
- [ ] Gọi /health từ trình duyệt Frontend thành công.
- [ ] Layout hiển thị ổn ở kích thước 1366×768 và 1920×1080.
- [ ] npm run lint thành công.
- [ ] npm run build thành công.

Chỉ đánh dấu các mục đã kiểm tra thực tế.