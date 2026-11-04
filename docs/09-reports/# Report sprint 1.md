# Report sprint 1

**Dự án:** Hệ thống Giám sát và Bảo trì Cơ sở Hạ tầng Tích hợp Thức tế Tăng cường  
**Sprint 1:** Phân tích nội dung đề tài  
**Thời gian thực hiện:** 9/10/2026 - 21/10/2026  

### Thành viên tham gia

| Tên thành viên | task | Tiến độ tham gia |
| :--- | :--- | :---: |
| Chu Thành Công | - Phân tích bối cảnh và vấn đề của hệ thống AR-IMMS.<br>- Xác định mục tiêu của dự án. | 100% |
| Phạm Hoàng Anh | - Xây dựng sơ đồ USE CASE tổng quát.<br>- Phác thảo kiến trúc hệ thống. | 100% |
| Trần Chí Vỉnh | - Xác định phạm vi dự án.<br>- Xác định các tác nhân của hệ thống. | 100% |
| Trần Anh Khôi | - Xây dựng yêu cầu chức năng | 100% |
| Vũ Minh Nhật | - Xây dựng yêu cầu phi chức năng | 80% |

### 1. Mục tiêu Sprint 1
Hoàn thành phân tích bối cảnh mục tiêu, phạm vi, tác nhân và yêu cầu chức năng của hệ thống AR-IMMS, xây dựng Use Case tổng quát và kiến trúc sơ bộ.

### 2. Kết quả

| Type | Key | Summary | Assignee | Priority | Status | Updated |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| Task | AI-2 | Phân tích bối cảnh và vấn đề của hệ thống AR-IMMS | Công Chu | Medium | Done | 24 Oct 2026, 22:00 |
| Task | AI-3 | Xác định mục tiêu của dự án | Công Chu | Medium | Done | 25 Oct 2026, 21:44 |
| Task | AI-4 | Xác định phạm vi dự án | Vỉnh Chí | Medium | Done | 28 Oct 2026, 23:51 |
| Task | AI-5 | Xác định các tác nhân của hệ thống | Vỉnh Chí | Medium | Done | 28 Oct 2026, 23:51 |
| Task | AI-6 | Xây dựng yêu cầu chức năng | Khôi Trần | Medium | Done | 28 Oct 2026, 23:41 |
| Task | AI-7 | Xây dựng yêu cầu phi chức năng | Minh Nhật | Medium | Done | 27 Oct 2026, 21:48 |
| Task | AI-8 | Xây dựng sơ đồ Use Case tổng quát | Hoàng anh phạm | Medium | Done | 28 Oct 2026, 17:36 |
| Task | AI-9 | ERD | Hoàng anh phạm | Medium | Done | 29 Oct 2026, 00:19 |

Nhóm đã xây dựng bộ tài liệu phân tích ban đầu cho AR-IMMS. Các vấn đề trọng tâm được xác định gồm sự tách biệt giữa dữ liệu giám sát và vị trí thiết bị vật lý, khó khăn trong tra cứu thông tin tại hiện trường và nhu cầu liên kết cảnh báo với công việc bảo trì.

Cấu trúc hạ tầng được xác định theo mô hình Site → Room → Rack → Node/Server → Container/Workload. Hệ thống phục vụ ba nhóm người dùng chính: Administrator, Operator và Technician.

Các tài liệu chức năng, phi chức năng, Use Case và kiến trúc được sử dụng làm đầu vào cho thiết kế cơ sở dữ liệu, API và phân chia công việc phát triển trong sprint tiếp theo.