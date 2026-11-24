# AR-IMMS – Telemetry Query API

## 1. Tổng quan

Backend cung cấp hai API để Web Portal truy vấn dữ liệu giám sát của từng Node:

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/telemetry/nodes/{node_id}/latest` | Lấy dữ liệu mới nhất |
| GET | `/telemetry/nodes/{node_id}/history` | Lấy lịch sử theo khoảng thời gian |

Các API dành cho Web Portal sử dụng Bearer JWT.

Các role được phép truy vấn:
- Administrator
- Operator
- Technician

## 2. Authentication

Gửi JWT trong HTTP header:

```http
Authorization: Bearer <access_token>
```

Ví dụ:

```http
GET /telemetry/nodes/{node_id}/latest
Authorization: Bearer eyJ...
```

Không sử dụng Agent certificate hoặc `X-Agent-Key` cho hai API truy vấn này.

## 3. Latest Telemetry

### Request

```http
GET /telemetry/nodes/{node_id}/latest
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| node_id | UUID | Yes | ID của Node |

Quy tắc chọn dữ liệu mới nhất:

1. `measured_at` giảm dần.
2. Nếu trùng `measured_at`, dùng `received_at` giảm dần.
3. Nếu vẫn trùng, dùng `id` giảm dần.

### Response 200

```json
{
  "node_id": "0fa96124-f0ab-4cb6-8919-8fcd4c8c6fad",
  "server_time": "2026-11-24T08:00:00+00:00",
  "latest": {
    "id": "6d2c3b31-6eaf-45e7-bd5a-2c5e3aaf43d0",
    "message_id": "c2e50e44-f789-4e1c-a8f4-abc123456789",
    "node_id": "0fa96124-f0ab-4cb6-8919-8fcd4c8c6fad",
    "measured_at": "2026-11-24T07:59:55+00:00",
    "received_at": "2026-11-24T07:59:56+00:00",
    "cpu_percent": 45.5,
    "memory_percent": 68.2,
    "disk_percent": 72.0
  },
  "monitoring": {
    "connection_status": "online",
    "data_status": "fresh",
    "last_received_at": "2026-11-24T07:59:56+00:00",
    "last_measured_at": "2026-11-24T07:59:55+00:00",
    "seconds_since_received": 4,
    "seconds_since_measured": 5,
    "stale_after_seconds": 30,
    "offline_after_seconds": 90
  },
  "poll_interval_seconds": 5
}
```

Nếu Node tồn tại nhưng chưa có Telemetry:

```json
{
  "node_id": "0fa96124-f0ab-4cb6-8919-8fcd4c8c6fad",
  "latest": null
}
```

Đây chỉ là phần minh họa trạng thái `latest`; response thực tế vẫn có các trường `server_time`, `monitoring` và `poll_interval_seconds`.

## 4. Telemetry History

### Request

```http
GET /telemetry/nodes/{node_id}/history?start=2026-11-24T00:00:00Z&end=2026-11-25T00:00:00Z&limit=100
```

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| node_id | UUID | Yes | – | ID của Node |
| start | ISO 8601 datetime | Yes | – | Thời điểm bắt đầu |
| end | ISO 8601 datetime | Yes | – | Thời điểm kết thúc |
| limit | Integer | No | 1000 | Số bản ghi tối đa |

Điều kiện:
- `start` và `end` phải có múi giờ.
- `start` phải nhỏ hơn `end`.
- `limit` nằm trong khoảng 1–1000.
- Lọc theo `measured_at` trong khoảng `[start, end)`.
- Kết quả được sắp xếp tăng dần theo `measured_at`, `received_at`, `id`.

### Response 200

```json
{
  "node_id": "0fa96124-f0ab-4cb6-8919-8fcd4c8c6fad",
  "start": "2026-11-24T00:00:00+00:00",
  "end": "2026-11-25T00:00:00+00:00",
  "limit": 100,
  "count": 2,
  "limit_reached": false,
  "items": [
    {
      "id": "6d2c3b31-6eaf-45e7-bd5a-2c5e3aaf43d0",
      "message_id": "c2e50e44-f789-4e1c-a8f4-abc123456789",
      "node_id": "0fa96124-f0ab-4cb6-8919-8fcd4c8c6fad",
      "measured_at": "2026-11-24T07:59:55+00:00",
      "received_at": "2026-11-24T07:59:56+00:00",
      "cpu_percent": 45.5,
      "memory_percent": 68.2,
      "disk_percent": 72.0
    },
    {
      "id": "8c5f1a12-1234-4567-8910-123456789abc",
      "message_id": "d2e50e44-f789-4e1c-a8f4-abc123456789",
      "node_id": "0fa96124-f0ab-4cb6-8919-8fcd4c8c6fad",
      "measured_at": "2026-11-24T08:00:00+00:00",
      "received_at": "2026-11-24T08:00:01+00:00",
      "cpu_percent": 50.0,
      "memory_percent": 65.0,
      "disk_percent": 73.0
    }
  ]
}
```

`limit_reached` bằng true khi số bản ghi trả về bằng `limit`. Trường này không khẳng định chắc chắn còn bản ghi tiếp theo.

Nếu không có dữ liệu trong khoảng thời gian:

```json
{
  "count": 0,
  "items": []
}
```

Các trường khác vẫn được trả về theo response schema.

## 5. Units và timestamps

| Field | Unit |
|---|---|
| cpu_percent | % |
| memory_percent | % |
| disk_percent | % |
| seconds_since_received | seconds |
| seconds_since_measured | seconds |
| poll_interval_seconds | seconds |

Timestamp được trả về theo ISO 8601 có múi giờ. Frontend nên parse timestamp thành Date và hiển thị theo múi giờ của người dùng.

Không dùng `received_at` thay cho `measured_at` khi vẽ biểu đồ lịch sử.

## 6. HTTP status codes

| Code | Ý nghĩa |
|---|---|
| 200 | Truy vấn thành công, kể cả khi chưa có Telemetry |
| 400 | UUID, timestamp hoặc limit không hợp lệ |
| 401 | Thiếu JWT hoặc JWT không hợp lệ |
| 403 | Role không được phép truy vấn |
| 404 | Không tìm thấy Node |
| 503 | Database hoặc dịch vụ tạm thời không khả dụng |
## 7. Frontend integration

### Lấy Telemetry mới nhất

```javascript
const latestResponse = await fetch(
  `${API_BASE_URL}/telemetry/nodes/${nodeId}/latest`,
  {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      Accept: "application/json",
    },
  }
);

if (!latestResponse.ok) {
  throw new Error(`Request failed: ${latestResponse.status}`);
}

const latestData = await latestResponse.json();
```

### Lấy lịch sử Telemetry

```javascript
const params = new URLSearchParams({
  start: "2026-11-24T00:00:00Z",
  end: "2026-11-25T00:00:00Z",
  limit: "100",
});

const historyResponse = await fetch(
  `${API_BASE_URL}/telemetry/nodes/${nodeId}/history?${params}`,
  {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      Accept: "application/json",
    },
  }
);

if (!historyResponse.ok) {
  throw new Error(`Request failed: ${historyResponse.status}`);
}

const historyData = await historyResponse.json();
const history = historyData.items;
```