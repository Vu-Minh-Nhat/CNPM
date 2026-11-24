# Report sprint 4

**Dự án:** Hệ thống Giám sát và Bảo trì Cơ sở Hạ tầng Tích hợp Thực tế Tăng cường

## 1. Thông tin chung về sprint
* **Sprint:** Sprint 4 - Tiếp tục backend
* **Thời gian thực hiện:** 10/11/2026 - 24/11/2026

## 2. Công việc và tiến độ

**Thành viên tham gia:**

| Tên thành viên | Task | Tiến độ tham gia |
| :--- | :--- | :---: |
| Chu Thành Công | - Thiết kế và triển khai cấu trúc lưu trữ Telemetry.<br>- Hiển thị Telemetry trên Web Portal, xác định và hiển thị trạng thái kết nối Node. | 100% |
| Trần Anh Khôi | - Xác thực Agent và kiểm soát quyền gửi Telemetry.<br>- Xây dựng API truy vấn Telemetry mới nhất và lịch sử. | 100% |
| Trần Chí Vỉnh | - Xây dựng API tiếp nhận và lưu Telemetry. | 100% |
| Phạm Hoàng Anh | - Xây dựng Collector Agent thu thập CPU, RAM và Disk. | 100% |
| Vũ Minh Nhật | | |

## 3. Kết quả

| Type | Key | Summary | Assignee | Priority | Status | Updated |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Task | AI-48 | Hiển thị Telemetry trên Web Portal, xác định và hiển thị trạng thái kết nối Node | Công Chu | Medium | Done | 17 Nov 2026, 18:12 |
| Task | AI-47 | Xây dựng API truy vấn Telemetry mới nhất và lịch sử | Khôi Trần | Medium | Done | 16 Nov 2026, 20:32 |
| Task | AI-46 | Xây dựng Collector Agent thu thập CPU, RAM và Disk | Hoàng anh phạm | Medium | Done | 12 Nov 2026, 00:14 |
| Task | AI-45 | Xây dựng API tiếp nhận và lưu Telemetry | Vỉnh Chí | Medium | Done | 16 Nov 2026, 21:38 |
| Task | AI-44 | Xác thực Agent và kiểm soát quyền gửi Telemetry | Khôi Trần | Medium | Done | 16 Nov 2026, 19:53 |
| Task | AI-43 | Thiết kế và triển khai cấu trúc lưu trữ Telemetry | Công Chu | Medium | Done | 11 Nov 2026, 17:14 |

Trong Sprint 4 này, nhóm đã tập trung triển khai toàn bộ các hạng mục công việc xoay quanh tầng xử lý dữ liệu và giám sát hệ thống (Backend & Telemetry), cụ thể:

* **Thiết kế và lưu trữ dữ liệu chuyên sâu:** Nhóm đã hoàn thiện việc thiết kế và xây dựng thành công cấu trúc lưu trữ Telemetry trên cơ sở dữ liệu, đồng thời phát triển hoàn chỉnh các API tiếp nhận, lưu trữ dữ liệu, cũng như các API hỗ trợ truy vấn thông tin Telemetry mới nhất và lịch sử.
* **Xây dựng Collector Agent thu thập thông số:** Đã phát triển thành công Collector Agent chuyên trách việc thu thập các chỉ số tài nguyên phần cứng cốt lõi của hệ thống gồm CPU, RAM và Disk một cách ổn định và chính xác.
* **Bảo mật và kiểm soát quyền hạn:** Thiết lập cơ chế xác thực Agent an toàn, áp dụng các biện pháp kiểm soát quyền gửi dữ liệu Telemetry chặt chẽ nhằm đảm bảo tính toàn vẹn và bảo mật cho hệ thống truyền tải thông tin.
* **Trực quan hóa và quản lý trạng thái kết nối Node:** Hoàn thiện giao diện trực quan hiển thị thông số Telemetry trực tiếp trên Web Portal, đồng thời xây dựng tính năng nhận diện, xác định và hiển thị chính xác trạng thái kết nối mạng của từng Node trên hệ thống.