# AR-IMMS Mobile

Ứng dụng Expo cho đăng nhập, quét QR gắn với Node, xem tài sản và telemetry, cảnh báo và ticket được giao. Lớp thông tin hiển thị cố định trên camera sau khi quét; chưa xác nhận theo dõi marker trong không gian AR.

## Chuẩn bị

- Node.js và npm phù hợp với dependencies trong `package.json`; điện thoại Android có Expo Go và quyền camera.
- Backend, PostgreSQL và dữ liệu mẫu theo [README backend](../backend-python/README.md). Để xem telemetry/cảnh báo mới, chạy Agent và Alert Worker.
- Điện thoại và máy tính cùng mạng nội bộ. Lấy IPv4 của máy chạy backend bằng `ipconfig`. Địa chỉ `localhost` trên điện thoại chỉ chính điện thoại.

## Cài đặt và cấu hình

Trong PowerShell tại thư mục `mobile`:

```powershell
npm ci
Copy-Item .env.example .env
notepad .env
```

Điền địa chỉ có thể truy cập từ điện thoại, ví dụ `EXPO_PUBLIC_API_BASE_URL=http://<IP_MAY_BACKEND>:5002`. Không đưa token hoặc mật khẩu vào file mẫu. Nếu đổi file `.env`, khởi động lại Expo.

Chạy backend cho phép kết nối LAN theo hướng dẫn backend; `run_mobile.bat` sử dụng `.env.migration` và lắng nghe trên tất cả địa chỉ mạng. Chỉ sử dụng trên mạng thử nghiệm tin cậy, cấu hình tường lửa phù hợp. Máy chủ Flask trong ví dụ dùng cho phát triển.

## Chạy và kiểm tra

```powershell
npm run typecheck
npx expo start -c
```

Mở Expo Go trên điện thoại, quét mã QR do Expo in trong terminal, sau đó đăng nhập bằng tài khoản đã seed. Quét QR marker khác trong màn hình ứng dụng để tìm Node; QR Expo dùng để mở app, không phải marker thiết bị.

Marker phải được Administrator tạo qua `POST /markers`, loại `QR`, gắn với Node. Nội dung QR phải chính xác là `identifier` đã đăng ký. Trên màn hình Node có thể xem telemetry, cảnh báo và ticket trong phạm vi tài khoản; Technician được giao có thể xử lý và gửi duyệt.

Nếu không kết nối được: kiểm tra backend `/health` trên máy chủ, địa chỉ IP trong `.env`, Wi-Fi/tường lửa, rồi khởi động lại Expo. Nếu không tìm thấy marker, kiểm tra identifier, loại QR và trạng thái hoạt động. Không chia sẻ JWT hoặc key khi gửi log.

## Giới hạn bàn giao

- Cần thêm bằng chứng kiểm thử trên thiết bị thật, đặc biệt mất mạng, phiên hết hạn và xung đột ticket.
- Bằng chứng ticket hiện là văn bản hoặc đường dẫn; không suy ra tệp đích đã được bảo vệ quyền.
- Chưa có hướng dẫn build APK/AAB đã được kiểm chứng trong bản này; Expo Go dùng cho demo, không phải bản phát hành production.
