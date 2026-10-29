# AR-IMMS

## Giới thiệu

**AR-IMMS — AR-Integrated Infrastructure Monitoring and
Maintenance System** là hệ thống giám sát và bảo trì cơ sở
hạ tầng tích hợp thực tế tăng cường.

Hệ thống liên kết thiết bị vật lý với telemetry, cảnh báo
và quy trình bảo trì. Web Portal hỗ trợ quản lý tập trung,
còn ứng dụng Mobile AR giúp kỹ thuật viên nhận diện
và tra cứu thông tin thiết bị ngay tại hiện trường.

Dự án được triển khai và đánh giá trên Mini Data Center Testbed.

## Bài toán cần giải quyết

- Dữ liệu giám sát tách biệt với vị trí thiết bị vật lý.
- Kỹ thuật viên mất thời gian đối chiếu để tìm đúng máy chủ.
- Telemetry, log và lịch sử bảo trì chưa được liên kết thuận tiện.
- Khó theo dõi xuyên suốt từ cảnh báo đến kết quả bảo trì.

## Người sử dụng

| Vai trò | Trách nhiệm chính |
|---|---|
| Administrator | Quản lý tài khoản, phân quyền, cấu hình, sức khỏe hệ thống và audit |
| Operator | Quản lý hạ tầng, giám sát, xử lý cảnh báo, phân công và phê duyệt đóng ticket |
| Technician | Nhận ticket, quét AR, kiểm tra thiết bị và cập nhật kết quả bảo trì |

Hệ thống giám sát tự động thực hiện thu thập telemetry,
phát hiện bất thường, cập nhật cảnh báo và xử lý kết nối.

## Các tính năng dự kiến

| Nhóm tính năng | Nội dung |
|---|---|
| Xác thực và phân quyền | Đăng nhập, quản lý tài khoản và RBAC |
| Quản lý hạ tầng | Site, Room, Rack, Node/Server và Workload |
| Digital Twin | Biểu diễn vị trí, quan hệ và trạng thái tài sản |
| Giám sát thời gian thực | CPU, RAM, network và trạng thái container |
| Cảnh báo | Phát hiện vượt ngưỡng, mất kết nối và chống cảnh báo trùng |
| Bảo trì | Tạo, phân công, cập nhật và phê duyệt đóng ticket |
| Mobile AR | Nhận diện QR/ArUco và hiển thị thông tin thiết bị |
| Vòng đời tài sản | Thông số phần cứng, bảo hành và lịch sử bảo trì |
| Báo cáo | Telemetry lịch sử, xu hướng tài nguyên và phân tích năng lượng |
| Audit | Ghi nhận và truy vết thao tác quan trọng |

Danh sách trên mô tả phạm vi sản phẩm.
Tình trạng triển khai được theo dõi trên Jira và các Pull Request.

## Cấu trúc hạ tầng

```text
Site
└── Room
    └── Rack
        └── Node / Server
            └── Container / Workload
```

## Kiến trúc tổng quan

```mermaid
flowchart LR
    NODE["Mini Data Center Testbed"] --> AGENT["Collector Agent"]
    AGENT -->|"Telemetry qua kết nối mTLS"| BACKEND["NestJS Backend"]

    BACKEND <-->|"Lưu và truy vấn dữ liệu"| DB["Database"]

    WEB["Next.js Web Portal"] <-->|"REST API / HTTPS"| BACKEND
    MOBILE["React Native Mobile AR"] <-->|"REST API / HTTPS"| BACKEND

    BACKEND --> GATEWAY["Socket.IO Gateway"]
    GATEWAY -->|"Dữ liệu thời gian thực"| WEB
    GATEWAY -->|"Dữ liệu thời gian thực"| MOBILE
```

Sơ đồ thể hiện kiến trúc dự kiến.
Chi tiết triển khai phải được đối chiếu với mã nguồn hiện có.

## Công nghệ

| Thành phần | Công nghệ định hướng |
|---|---|
| Backend | NestJS, TypeScript |
| Web Portal | Next.js |
| Mobile AR | React Native trên Android |
| Real-time | Socket.IO |
| Database | PostgreSQL và thiết kế lưu trữ time-series phù hợp |
| Workload thử nghiệm | Docker |
| Xác thực người dùng | JWT |
| Phân quyền | RBAC |
| Xác thực Agent | mTLS |
| Quản lý mã nguồn | Git, GitHub |
| Quản lý công việc | Jira |

Phiên bản và dependency cụ thể được xác định trong
các file cấu hình của từng thành phần.

## Luồng nghiệp vụ chính

1. Agent thu thập và gửi telemetry của node.
2. Backend kiểm tra, lưu dữ liệu và cập nhật Web/Mobile.
3. Hệ thống phát hiện bất thường và tạo cảnh báo.
4. Operator tạo ticket và phân công Technician.
5. Technician nhận diện thiết bị bằng Mobile AR.
6. Technician kiểm tra và ghi nhận kết quả bảo trì.
7. Operator kiểm tra và phê duyệt đóng ticket.
8. Hệ thống lưu lịch sử và audit.

## Các tiêu chí quan trọng

- Chu kỳ telemetry mặc định là **5 giây** và cấu hình được.
- Node được xác định không khả dụng khi không nhận telemetry
  trong **hơn 90 giây**.
- Node mới phải bắt đầu streaming và xuất hiện trong Digital Twin
  trong **tối đa 5 phút** kể từ lúc đăng ký.
- Dữ liệu cũ phải được phân biệt với dữ liệu hiện tại.
- Thao tác có thể gây gián đoạn phải có kiểm tra quyền,
  xác nhận và audit nếu được cung cấp.

Đây là tiêu chí cần kiểm chứng, không phải tuyên bố
rằng hệ thống đã đạt tất cả yêu cầu.

## Thiết lập môi trường Backend

### 1. Tải mã nguồn

Thay các giá trị trong dấu `<...>` bằng thông tin repository:

```bash
git clone <repository-url>
cd <repository-folder>
```

Nếu Backend nằm trong thư mục con, chuyển vào thư mục
chứa `package.json` của Backend trước khi chạy lệnh.

### 2. Cài dependency

Sử dụng package manager tương ứng với lockfile của repository.

Ví dụ, nếu dự án sử dụng npm:

```bash
npm install
```

### 3. Cấu hình môi trường

- Thiết lập kết nối database.
- Thiết lập cấu hình JWT.
- Thiết lập các giá trị môi trường mà ứng dụng yêu cầu.
- Nếu repository có `.env.example`, sao chép thành `.env`
  và điền giá trị phù hợp.
- Chạy migration theo hướng dẫn và công cụ database
  được sử dụng trong repository.

Không đưa mật khẩu, token, khóa riêng hoặc chứng thư
có thông tin bí mật lên GitHub.

### 4. Chạy ứng dụng

Xem các script hiện có:

```bash
npm run
```

Nếu `package.json` có script `start:dev`, chạy:

```bash
npm run start:dev
```

Cổng và địa chỉ truy cập được xác định theo cấu hình
và thông báo khi ứng dụng khởi động.

## Kiểm thử

Sử dụng các script kiểm thử được khai báo trong `package.json`.

Ví dụ, nếu repository có các script tương ứng:

```bash
npm run test
npm run test:e2e
npm run build
```

Các nhóm kiểm thử chính:

- Xác thực và phân quyền.
- Quan hệ tài sản và dữ liệu đầu vào.
- Tiếp nhận và truy vấn telemetry.
- Streaming và phục hồi kết nối.
- Cảnh báo và quy trình ticket.
- Nhận diện marker.
- Audit và bảo mật.

## Tài liệu dự án

Bộ tài liệu phân tích gồm:

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

Tài liệu kiến trúc, Screen Flow, test case và hướng dẫn
triển khai được bổ sung theo tiến độ dự án.

## Quy trình làm việc nhóm

1. Lấy phiên bản mới nhất của nhánh chung.
2. Tạo branch riêng cho công việc.
3. Phát triển và kiểm thử.
4. Push branch lên GitHub.
5. Tạo Pull Request.
6. Review và xử lý góp ý trước khi merge.

Ví dụ tên branch:

```text
feature/rbac
feature/telemetry
fix/token-validation
docs/ai-7
```

Không push thông tin bí mật hoặc file môi trường cá nhân.
Nhánh đích của Pull Request tuân theo quy ước của nhóm.

## Giới hạn

- Đánh giá trên testbed, chưa triển khai vào Data Center thực tế.
- Khả năng thu thập metric phụ thuộc thiết bị và quyền truy cập.
- Mobile AR hướng tới Android và marker đã đăng ký.
- Phân tích điện năng/PUE cần dữ liệu đầu vào phù hợp.
- Dữ liệu mô phỏng phải được ghi rõ.
- Không bao gồm tự động sửa chữa phần cứng hoặc
  điều khiển từ xa không giới hạn.

## Quản lý công việc

[Jira — AR-IMMS](https://phamvanut12121958.atlassian.net/jira/software/projects/AI/boards/2/backlog)
