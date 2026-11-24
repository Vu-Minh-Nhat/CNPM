# Task 49 — Alert & Ticket Test Cases

## 1. Mục tiêu kiểm thử

Kiểm tra các quy tắc nghiệp vụ, quyền truy cập và vòng đời Alert/Ticket đã thống nhất trong Task 49.

Phạm vi kiểm thử:

- Alert lifecycle.
- Ticket lifecycle.
- Telemetry freshness.
- Duplicate telemetry.
- Alert deduplication.
- RBAC.
- API validation.
- Error handling.
- Các tình huống biên.

## 2. Alert Test Cases

| ID | Test case | Expected result |
|---|---|---|
| ALT-001 | Telemetry thỏa điều kiện alert | Tạo alert đúng asset, thời gian và nguyên nhân |
| ALT-002 | Cùng một active incident gửi lại | Không tạo duplicate alert |
| ALT-003 | Điều kiện alert vẫn còn | Alert tiếp tục ở trạng thái active |
| ALT-004 | User acknowledge alert | Alert chuyển sang `ACKNOWLEDGED` |
| ALT-005 | Acknowledge nhưng nguyên nhân chưa hết | Alert không chuyển sang `RECOVERED` |
| ALT-006 | Điều kiện recovery được thỏa mãn | Alert chuyển sang `RECOVERED` |
| ALT-007 | Alert đã recovered | Không tạo lại duplicate cho cùng incident nếu policy không yêu cầu reopen |
| ALT-008 | Telemetry cũ | Không được coi là telemetry hiện tại |
| ALT-009 | Telemetry quá thời gian offline | Node được đánh dấu unavailable theo policy |
| ALT-010 | Telemetry gửi lại cùng `message_id` | Không tạo duplicate telemetry |
| ALT-011 | Cùng identity nhưng nội dung khác | Backend xử lý conflict theo duplicate policy |
| ALT-012 | User không đủ quyền acknowledge | API trả `403` |

## 3. Ticket Test Cases

| ID | Test case | Expected result |
|---|---|---|
| TKT-001 | Operator tạo ticket hợp lệ | Ticket được tạo với trạng thái `NEW` |
| TKT-002 | Operator phân công Technician active | Ticket chuyển `NEW → ASSIGNED` |
| TKT-003 | Technician mở ticket được giao | Có thể xem ticket |
| TKT-004 | Technician cập nhật tiến độ | Cập nhật thành công |
| TKT-005 | Technician cập nhật kết quả | Dữ liệu kết quả được lưu |
| TKT-006 | Technician gửi ticket chờ duyệt | Ticket chuyển `IN_PROGRESS → PENDING_APPROVAL` |
| TKT-007 | Technician cố đóng ticket | Bị từ chối |
| TKT-008 | Operator kiểm tra kết quả hợp lệ | Ticket chuyển `PENDING_APPROVAL → CLOSED` |
| TKT-009 | Operator trả lại ticket | Ticket chuyển `PENDING_APPROVAL → IN_PROGRESS` |
| TKT-010 | Trả lại ticket không có lý do | API trả lỗi validation |
| TKT-011 | Ticket đóng nhưng alert vẫn active | Ticket `CLOSED`, alert vẫn giữ trạng thái active |
| TKT-012 | Phân công Technician không active | Không cho phép phân công |

## 4. RBAC Test Cases

| ID | Test case | Expected result |
|---|---|---|
| RBAC-001 | Gọi API không có JWT | `401 Unauthorized` |
| RBAC-002 | Gọi API bằng JWT không hợp lệ | `401 Unauthorized` |
| RBAC-003 | JWT đã hết hạn | `401 Unauthorized` |
| RBAC-004 | User đăng nhập nhưng không đủ quyền | `403 Forbidden` |
| RBAC-005 | Technician cố tạo ticket | Bị từ chối |
| RBAC-006 | Technician cố approve-close | Bị từ chối |
| RBAC-007 | Technician cập nhật ticket không được giao | Bị từ chối theo scope |
| RBAC-008 | Operator truy cập resource ngoài scope | Bị từ chối theo scope |
| RBAC-009 | Backend kiểm tra role từ account hiện tại | Không tin role do Frontend gửi |
| RBAC-010 | Account bị disable gọi protected API | Không được phép truy cập |

## 5. API Validation Test Cases

| ID | Test case | Expected result |
|---|---|---|
| API-001 | Thiếu field bắt buộc khi tạo ticket | `400 Bad Request` |
| API-002 | Field có kiểu dữ liệu sai | `400 Bad Request` |
| API-003 | Giá trị enum không hợp lệ | `400 Bad Request` |
| API-004 | Resource không tồn tại | `404 Not Found` |
| API-005 | Tạo resource bị duplicate | `409 Conflict` |
| API-006 | Transition không hợp lệ | API từ chối request |
| API-007 | Request hợp lệ | API trả `200` hoặc `201` tùy operation |
| API-008 | Không gửi Content-Type phù hợp | API xử lý theo contract hoặc trả validation error |

## 6. Freshness Test Cases

| ID | Test case | Expected result |
|---|---|---|
| FRESH-001 | Telemetry mới trong ngưỡng freshness | Được coi là dữ liệu hiện tại |
| FRESH-002 | Telemetry quá 30 giây | Được đánh dấu stale theo Task 49 |
| FRESH-003 | Không có telemetry quá 90 giây | Node được coi là mất kết nối |
| FRESH-004 | Telemetry stale nhưng chưa offline | UI phân biệt stale với disconnected |
| FRESH-005 | Telemetry timestamp ở quá khứ | Không tự động cập nhật thành thời điểm hiện tại |

## 7. Duplicate và Late Data Test Cases

| ID | Test case | Expected result |
|---|---|---|
| DATA-001 | Retry cùng `message_id` | Không tạo duplicate telemetry |
| DATA-002 | Retry cùng nội dung | Trả kết quả theo duplicate policy |
| DATA-003 | Cùng identity nhưng payload khác | Xử lý conflict |
| DATA-004 | Telemetry đến muộn | Xử lý theo late-data policy |
| DATA-005 | Telemetry cũ làm thỏa threshold | Không tạo alert sai nếu dữ liệu không còn hợp lệ |
| DATA-006 | Nhiều message cùng active incident | Chỉ có alert theo incident deduplication rule |

## 8. Ticket Lifecycle Test Cases

Các transition hợp lệ:

```text
NEW
 ↓
ASSIGNED
 ↓
IN_PROGRESS
 ↓
PENDING_APPROVAL
 ↓
CLOSED