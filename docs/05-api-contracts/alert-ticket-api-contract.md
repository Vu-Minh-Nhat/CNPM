# Task 49 — Alert & Ticket API Contract

## 1. Quy ước chung

### 1.1 Format

- Request và response sử dụng JSON.
- Content-Type: `application/json`.
- API được bảo vệ bằng JWT Bearer đối với endpoint yêu cầu xác thực.
- Backend là nơi quyết định quyền truy cập.
- Không tin role do Frontend gửi lên.
- Backend phải kiểm tra scope của tài nguyên trước khi cho phép thao tác.

### 1.2 Bảo mật

API không được trả về:

- password;
- password hash;
- JWT;
- secret;
- Agent credential.

## 2. HTTP Status Code

| Status | Ý nghĩa |
|---|---|
| 200 | Request thành công |
| 201 | Tạo resource thành công |
| 400 | Request không hợp lệ |
| 401 | Thiếu, sai hoặc hết hạn JWT; account không hợp lệ |
| 403 | Đã xác thực nhưng không đủ quyền |
| 404 | Không tìm thấy resource |
| 409 | Conflict, ví dụ duplicate hoặc trạng thái xung đột |

## 3. Alert API

### 3.1 Lấy danh sách alert

```http
GET /alerts