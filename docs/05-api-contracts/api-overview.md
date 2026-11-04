# Tổng quan API Backend AR-IMMS

## 1. Mục đích

Cung cấp thông tin API để các thành viên tích hợp Web Portal,
Mobile và kiểm thử Backend.

Tài liệu liên quan:

- AI-30: Đăng nhập và xác thực JWT.
- AI-31: Phân quyền RBAC.
- AI-32: API quản lý Site, Room, Rack và Server.
- AI-33: Kiểm thử API và cập nhật tài liệu kỹ thuật.

Danh sách dưới đây mô tả các endpoint hiện có.
Kết quả kiểm thử được ghi riêng trong báo cáo kiểm thử.

## 2. Địa chỉ và công cụ

| Thành phần | Địa chỉ mặc định khi phát triển |
|---|---|
| Backend | http://localhost:3000 |
| Swagger UI | http://localhost:3000/api |
| OpenAPI JSON | http://localhost:3000/api-json |
| Web Portal | http://localhost:3001 |

Địa chỉ thực tế phụ thuộc cấu hình môi trường.

Trong tài liệu, đường dẫn API được viết tương đối
so với địa chỉ Backend.

## 3. Quy ước gọi API

- Dữ liệu gửi và nhận sử dụng JSON.
- Request có JSON body sử dụng Content-Type: application/json.
- API được bảo vệ yêu cầu JWT trong Authorization header.
- Giá trị vai trò phân biệt theo tên:
  Administrator, Operator và Technician.
- ID của tài sản sử dụng UUID.
- Mật khẩu và JWT trong ví dụ chỉ là giá trị minh họa.

Header xác thực:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 4. API công khai và xác thực

| Method | Endpoint | Chức năng | Quyền |
|---|---|---|---|
| GET | /health | Kiểm tra Backend đang phản hồi | Công khai |
| POST | /auth/login | Xác thực tài khoản và cấp JWT | Công khai |
| GET | /auth/me | Lấy thông tin tài khoản hiện tại | Cả ba vai trò |

### 4.1. Đăng nhập

Request:

```http
POST /auth/login
Content-Type: application/json
```

```json
{
  "email": "admin@arimms.local",
  "password": "YOUR_PASSWORD"
}
```

Response thành công — HTTP 200:

```json
{
  "accessToken": "YOUR_ACCESS_TOKEN",
  "role": "Administrator"
}
```

Tài khoản minh họa chỉ tồn tại khi database đã có
dữ liệu seed tương ứng.

Mật khẩu sử dụng giá trị đã thiết lập trên môi trường đó,
không có mật khẩu cố định chung cho mọi máy.

### 4.2. Xác minh tài khoản

Request:

```http
GET /auth/me
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Response thành công — HTTP 200:

```json
{
  "userId": "11111111-1111-4111-8111-111111111111",
  "email": "admin@arimms.local",
  "role": "Administrator"
}
```

Ứng dụng dùng thông tin này để hiển thị tài khoản
và menu theo vai trò.

Backend vẫn kiểm tra quyền riêng cho từng API.

### 4.3. Kiểm tra sức khỏe

GET /health xác nhận Backend đang phản hồi.

Kết quả này không tự chứng minh database, Agent,
telemetry hoặc toàn bộ chức năng nghiệp vụ đang hoạt động.

## 5. API quản lý tài khoản

Tất cả endpoint trong bảng yêu cầu vai trò Administrator.

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | /users | Xem danh sách tài khoản |
| POST | /users | Tạo tài khoản |
| PATCH | /users/:id/role | Thay đổi vai trò tài khoản |

### 5.1. Tạo tài khoản

Request body:

```json
{
  "email": "technician.new@arimms.local",
  "password": "REPLACE_WITH_A_STRONG_PASSWORD",
  "role": "Technician"
}
```

Quy tắc hiện tại:

- Email không được trùng.
- Mật khẩu tối thiểu 8 ký tự, tối đa 72 byte UTF-8.
- Vai trò phải thuộc ba giá trị hợp lệ.
- Response không được chứa password hash.

### 5.2. Thay đổi vai trò

Request:

```http
PATCH /users/:id/role
```

```json
{
  "role": "Operator"
}
```

Chỉ Administrator được thực hiện.

## 6. API quản lý hạ tầng

Các nhóm tài nguyên:

| Tài nguyên | Đường dẫn | Thực thể |
|---|---|---|
| Site | /sites | Địa điểm |
| Room | /rooms | Phòng |
| Rack | /racks | Tủ rack |
| Server | /servers | Node trong mô hình dữ liệu |

Mỗi nhóm cung cấp các thao tác sau:

| Method | Mẫu endpoint | Chức năng | Quyền |
|---|---|---|---|
| GET | /resource | Xem danh sách | Cả ba vai trò |
| GET | /resource/:id | Xem chi tiết | Cả ba vai trò |
| POST | /resource | Tạo mới | Administrator, Operator |
| PATCH | /resource/:id | Cập nhật | Administrator, Operator |
| DELETE | /resource/:id | Xóa | Administrator |

Thay resource bằng sites, rooms, racks hoặc servers.
Ví dụ: GET /sites và PATCH /servers/:id.

### 6.1. Tạo Site

```http
POST /sites
```

```json
{
  "code": "SITE-01",
  "name": "Mini Data Center"
}
```

### 6.2. Tạo Room

```http
POST /rooms
```

```json
{
  "siteId": "11111111-1111-4111-8111-111111111111",
  "code": "ROOM-01",
  "name": "Phòng máy số 1"
}
```

siteId phải là ID của Site đã tồn tại.

### 6.3. Tạo Rack

```http
POST /racks
```

```json
{
  "roomId": "22222222-2222-4222-8222-222222222222",
  "code": "RACK-01",
  "name": "Tủ rack số 1",
  "capacityU": 42
}
```

roomId phải tồn tại.
capacityU là số nguyên từ 1 đến 100 theo thiết kế hiện tại.

### 6.4. Tạo Server

```http
POST /servers
```

```json
{
  "rackId": "33333333-3333-4333-8333-333333333333",
  "code": "SERVER-01",
  "name": "Máy chủ thử nghiệm",
  "serialNumber": "SN-SERVER-01"
}
```

rackId phải tồn tại.
serialNumber là trường không bắt buộc.

Các UUID trong ví dụ phải được thay bằng ID thật
nhận từ API hoặc database của môi trường đang sử dụng.

### 6.5. Cập nhật tài sản

Sử dụng PATCH với các trường được hỗ trợ bởi DTO cập nhật.

Ví dụ:

```http
PATCH /sites/:id
```

```json
{
  "name": "Địa điểm đã cập nhật"
}
```

Thay đổi tài sản cha phải tham chiếu đến bản ghi tồn tại.
Nếu yêu cầu bị từ chối, dữ liệu cũ phải được giữ nguyên.

### 6.6. Xóa tài sản

Chỉ Administrator được xóa Site, Room, Rack và Server.

Không xóa bản ghi khi còn dữ liệu phụ thuộc
bị ràng buộc không cho phép xóa.

Ví dụ: xóa Site còn Room trả về 409.

## 7. API tổng hợp tài sản

| Method | Endpoint | Phạm vi |
|---|---|---|
| GET | /assets | Tra cứu Node và các quan hệ tài sản; cả ba vai trò |
| POST | /assets | Chưa triển khai xử lý ghi; Administrator, Operator được qua bước kiểm tra vai trò |
| PUT | /assets/:id | Chưa triển khai xử lý ghi; Administrator, Operator được qua bước kiểm tra vai trò |
| DELETE | /assets/:id | Chưa triển khai xử lý ghi; chỉ Administrator được qua bước kiểm tra vai trò |

Các thao tác ghi tại /assets hiện trả về 501
sau khi người gọi vượt qua bước xác thực và phân quyền.

Người thiếu quyền vẫn bị từ chối bằng 403.
Người chưa xác thực bị từ chối bằng 401.

Sử dụng /sites, /rooms, /racks và /servers
cho các thao tác CRUD đã triển khai.

## 8. Mã trạng thái

| Mã | Ý nghĩa và trường hợp sử dụng |
|---|---|
| 200 | Đọc, đăng nhập, cập nhật hoặc xóa thành công theo endpoint |
| 201 | Tạo bản ghi thành công ở các endpoint POST tạo dữ liệu |
| 400 | Dữ liệu không hợp lệ hoặc tham chiếu tài sản cha không tồn tại |
| 401 | Thiếu JWT, JWT không hợp lệ, hết hạn hoặc tài khoản không còn hợp lệ |
| 403 | Đã xác thực nhưng không có quyền |
| 404 | Không tìm thấy tài nguyên yêu cầu |
| 409 | Xung đột dữ liệu, mã trùng hoặc xóa bản ghi còn phụ thuộc |
| 501 | Endpoint đã có nhưng thao tác chưa được triển khai |

Thông báo lỗi cụ thể phụ thuộc endpoint.
Frontend nên xử lý theo mã trạng thái
và cung cấp thông báo phù hợp cho người sử dụng.

## 9. Kiểm thử bằng Swagger

1. Khởi động Backend.
2. Mở /api.
3. Thực hiện POST /auth/login bằng tài khoản hợp lệ.
4. Sao chép accessToken từ response.
5. Chọn Authorize và nhập token vào ô Bearer.
6. Gọi GET /auth/me để xác minh.
7. Kiểm tra các API theo từng vai trò.
8. Kiểm tra trường hợp thiếu token, sai token và thiếu quyền.

Không đưa token thật hoặc mật khẩu vào ảnh chụp,
repository hoặc báo cáo công khai.

## 10. Giới hạn và cập nhật

- Không tự suy ra endpoint từ tên chức năng trong SRS.
- API Workload, telemetry, cảnh báo, ticket và audit
  được bổ sung tài liệu khi có thiết kế hoặc triển khai tương ứng.
- Cơ chế logout hiện tại do Frontend xóa thông tin phiên;
  chưa có endpoint logout trong danh sách API đã đối chiếu.
- Khi thay đổi controller, DTO hoặc quyền truy cập,
  phải cập nhật tài liệu và ca kiểm thử liên quan.