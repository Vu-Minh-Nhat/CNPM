
from copy import deepcopy


def build_openapi():
    def ref(name):
        return {"$ref": f"#/components/schemas/{name}"}

    def array(name):
        return {"type": "array", "items": ref(name)}

    def object_schema(properties, required=None):
        return {
            "type": "object",
            "properties": properties,
            "required": list(properties) if required is None else required,
        }

    def input_schema(properties, required):
        schema = object_schema(properties, required)
        schema["additionalProperties"] = False
        return schema

    uuid = {"type": "string", "format": "uuid"}

    code = {
        "type": "string",
        "minLength": 1,
        "maxLength": 64,
        "pattern": r"\S",
    }

    name = {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "pattern": r"\S",
    }

    role = {
        "type": "string",
        "enum": ["Administrator", "Operator", "Technician"],
    }

    schemas = {}

    def nullable(schema_name):
        schema = deepcopy(schemas[schema_name])
        schema["nullable"] = True
        return schema

    schemas["Error"] = object_schema({
        "message": {"type": "string"},
        "error": {"type": "string"},
        "statusCode": {"type": "integer"},
    })

    schemas["Message"] = object_schema({
        "message": {"type": "string"},
    })

    # ------------------------------------------------------------------
    # Telemetry schemas
    # ------------------------------------------------------------------

    schemas["TelemetryInput"] = input_schema({
        "message_id": uuid,
        "node_id": uuid,
        "measured_at": {
            "type": "string",
            "format": "date-time",
            "description": "Thời điểm Agent đo dữ liệu, phải có múi giờ.",
        },
        "cpu_percent": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
        },
        "memory_percent": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
        },
        "disk_percent": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
        },
    }, [
        "message_id",
        "node_id",
        "measured_at",
        "cpu_percent",
        "memory_percent",
        "disk_percent",
    ])

    schemas["TelemetryRecord"] = object_schema({
        "id": uuid,
        "message_id": uuid,
        "node_id": uuid,
        "measured_at": {
            "type": "string",
            "format": "date-time",
            "description": "Thời điểm đo dữ liệu, theo ISO 8601.",
        },
        "received_at": {
            "type": "string",
            "format": "date-time",
            "description": "Thời điểm Backend nhận dữ liệu, theo ISO 8601.",
        },
        "cpu_percent": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Mức sử dụng CPU, đơn vị phần trăm (%).",
        },
        "memory_percent": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Mức sử dụng RAM, đơn vị phần trăm (%).",
        },
        "disk_percent": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Mức sử dụng Disk, đơn vị phần trăm (%).",
        },
    })

    schemas["TelemetryLatest"] = object_schema({
        "node_id": uuid,
        "server_time": {
            "type": "string",
            "format": "date-time",
        },
        "latest": nullable("TelemetryRecord"),
        "monitoring": object_schema({
            "connection_status": {
                "type": "string",
                "description": "Trạng thái kết nối của Node.",
                "example": "online",
            },
            "data_status": {
                "type": "string",
                "description": "Trạng thái mới/cũ của dữ liệu.",
                "example": "fresh",
            },
            "last_received_at": {
                "type": "string",
                "format": "date-time",
                "nullable": True,
            },
            "last_measured_at": {
                "type": "string",
                "format": "date-time",
                "nullable": True,
            },
            "seconds_since_received": {
                "type": "number",
                "nullable": True,
            },
            "seconds_since_measured": {
                "type": "number",
                "nullable": True,
            },
            "stale_after_seconds": {
                "type": "integer",
            },
            "offline_after_seconds": {
                "type": "integer",
            },
        }),
        "poll_interval_seconds": {
            "type": "integer",
            "minimum": 1,
        },
    })

    schemas["TelemetryHistory"] = object_schema({
        "node_id": uuid,
        "start": {
            "type": "string",
            "format": "date-time",
        },
        "end": {
            "type": "string",
            "format": "date-time",
        },
        "limit": {
            "type": "integer",
            "minimum": 1,
            "maximum": 1000,
        },
        "count": {
            "type": "integer",
            "minimum": 0,
        },
        "limit_reached": {
            "type": "boolean",
            "description": (
                "True khi số bản ghi trả về bằng limit; "
                "không khẳng định chắc chắn còn bản ghi tiếp theo."
            ),
        },
        "items": {
            "type": "array",
            "items": ref("TelemetryRecord"),
        },
    })

    # ------------------------------------------------------------------
    # Health and Authentication schemas
    # ------------------------------------------------------------------

    schemas["Health"] = object_schema({
        "status": {"type": "string", "example": "ok"},
        "service": {"type": "string", "example": "ar-imms-backend"},
        "timestamp": {"type": "string", "format": "date-time"},
        "uptimeSeconds": {"type": "integer", "minimum": 0},
    })

    schemas["LoginInput"] = object_schema({
        "email": {
            "type": "string",
            "example": "admin@arimms.local",
        },
        "password": {
            "type": "string",
            "format": "password",
        },
    })

    schemas["LoginResult"] = object_schema({
        "accessToken": {"type": "string"},
        "role": role,
    })

    schemas["CurrentUser"] = object_schema({
        "userId": uuid,
        "email": {"type": "string"},
        "role": role,
    })

    schemas["Account"] = object_schema({
        "id": uuid,
        "email": {"type": "string"},
        "role": role,
        "isActive": {"type": "boolean"},
    })

    schemas["CreateAccount"] = input_schema({
        "email": {
            "type": "string",
            "format": "email",
            "maxLength": 254,
        },
        "password": {
            "type": "string",
            "format": "password",
            "minLength": 8,
            "description": "Tối thiểu 8 ký tự, tối đa 72 byte UTF-8.",
        },
        "role": role,
    }, ["email", "password", "role"])

    schemas["ChangeRole"] = input_schema(
        {"role": role},
        ["role"],
    )

    # ------------------------------------------------------------------
    # Asset schemas
    # ------------------------------------------------------------------

    site_fields = {
        "id": uuid,
        "code": code,
        "name": name,
    }

    room_fields = {
        "id": uuid,
        "siteId": uuid,
        "code": code,
        "name": name,
    }

    rack_fields = {
        "id": uuid,
        "roomId": uuid,
        "code": code,
        "name": name,
        "capacityU": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
        },
    }

    node_fields = {
        "id": uuid,
        "rackId": uuid,
        "code": code,
        "name": name,
        "serialNumber": {
            "type": "string",
            "maxLength": 128,
            "nullable": True,
        },
    }

    schemas["Site"] = object_schema(site_fields)

    schemas["RoomSummary"] = object_schema(room_fields)

    schemas["Room"] = object_schema({
        **room_fields,
        "site": nullable("Site"),
    })

    schemas["RackSummary"] = object_schema(rack_fields)

    schemas["Rack"] = object_schema({
        **rack_fields,
        "room": nullable("RoomSummary"),
    })

    schemas["NodeSummary"] = object_schema(node_fields)

    schemas["Workload"] = object_schema({
        "id": uuid,
        "nodeId": uuid,
        "code": code,
        "name": name,
        "runtimeId": {
            "type": "string",
            "maxLength": 200,
            "nullable": True,
        },
    })

    schemas["AssetRack"] = object_schema({
        **rack_fields,
        "room": nullable("Room"),
    })

    schemas["Node"] = object_schema({
        **node_fields,
        "rack": nullable("AssetRack"),
        "workloads": array("Workload"),
    })

    schemas["RoomDetail"] = object_schema({
        **schemas["Room"]["properties"],
        "racks": array("RackSummary"),
    })

    schemas["RackDetail"] = object_schema({
        **schemas["Rack"]["properties"],
        "nodes": array("NodeSummary"),
    })

    # ------------------------------------------------------------------
    # Alert schemas
    # ------------------------------------------------------------------

    schemas["Alert"] = object_schema({
        "id": uuid,
        "node_id": uuid,
        "rule_id": {
            **uuid,
            "nullable": True,
        },
        "metric": {
            "type": "string",
            "enum": [
                "cpu_percent",
                "memory_percent",
                "disk_percent",
                "node_offline_seconds",
            ],
        },
        "operator": {
            "type": "string",
            "enum": [">", ">=", "<", "<="],
        },
        "threshold": {
            "type": "number",
            "nullable": True,
        },
        "triggered_value": {
            "type": "number",
            "nullable": True,
            "description": "Giá trị thực tế tại thời điểm kích hoạt Alert.",
        },
        "severity": {
            "type": "string",
            "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        },
        "status": {
            "type": "string",
            "enum": ["FIRING", "ACKNOWLEDGED", "RECOVERED"],
        },
        "message": {
            "type": "string",
        },
        "triggered_at": {
            "type": "string",
            "format": "date-time",
        },
        "acknowledged_by": {
            **uuid,
            "nullable": True,
            "description": "UUID tài khoản đã xác nhận Alert.",
        },
        "acknowledged_at": {
            "type": "string",
            "format": "date-time",
            "nullable": True,
        },
        "recovered_at": {
            "type": "string",
            "format": "date-time",
            "nullable": True,
        },
    })

    schemas["AlertPagination"] = object_schema({
        "page": {
            "type": "integer",
            "minimum": 1,
        },
        "page_size": {
            "type": "integer",
            "minimum": 1,
        },
        "total": {
            "type": "integer",
            "minimum": 0,
        },
        "total_pages": {
            "type": "integer",
            "minimum": 0,
        },
    })

    schemas["AlertList"] = object_schema({
        "items": array("Alert"),
        "pagination": ref("AlertPagination"),
    })

    # ------------------------------------------------------------------
    # Marker schemas - Task 58
    # ------------------------------------------------------------------

    schemas["Marker"] = object_schema({
        "id": uuid,
        "marker_type": {
            "type": "string",
            "minLength": 1,
            "maxLength": 32,
            "pattern": r"\S",
        },
        "identifier": {
            "type": "string",
            "minLength": 1,
            "maxLength": 128,
            "pattern": r"\S",
        },
        "node_id": uuid,
        "is_active": {
            "type": "boolean",
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
        },
        "updated_at": {
            "type": "string",
            "format": "date-time",
        },
    })

    schemas["CreateMarker"] = input_schema({
        "marker_type": {
            "type": "string",
            "minLength": 1,
            "maxLength": 32,
            "pattern": r"\S",
        },
        "identifier": {
            "type": "string",
            "minLength": 1,
            "maxLength": 128,
            "pattern": r"\S",
        },
        "node_id": uuid,
    }, [
        "marker_type",
        "identifier",
        "node_id",
    ])

    schemas["MarkerLookupResult"] = object_schema({
        "marker": ref("Marker"),
        "node": ref("Node"),
    })

    # ------------------------------------------------------------------
    # Resource definitions
    # ------------------------------------------------------------------

    resources = (
        (
            "sites",
            "Site",
            "Site",
            {
                "code": code,
                "name": name,
            },
            ["code", "name"],
        ),
        (
            "rooms",
            "Room",
            "RoomDetail",
            {
                "siteId": uuid,
                "code": code,
                "name": name,
            },
            ["siteId", "code", "name"],
        ),
        (
            "racks",
            "Rack",
            "RackDetail",
            {
                "roomId": uuid,
                "code": code,
                "name": name,
                "capacityU": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                },
            },
            ["roomId", "code", "name", "capacityU"],
        ),
        (
            "servers",
            "Node",
            "Node",
            {
                "rackId": uuid,
                "code": code,
                "name": name,
                "serialNumber": {
                    "type": "string",
                    "nullable": True,
                    "minLength": 1,
                    "maxLength": 128,
                    "pattern": r"\S",
                },
            },
            ["rackId", "code", "name"],
        ),
    )

    # ------------------------------------------------------------------
    # OpenAPI helper functions
    # ------------------------------------------------------------------

    def response(description, schema):
        return {
            "description": description,
            "content": {
                "application/json": {
                    "schema": schema,
                }
            },
        }

    error_names = {
        400: "Dữ liệu không hợp lệ.",
        401: "Chưa xác thực hoặc token không hợp lệ.",
        403: "Không đủ quyền.",
        404: "Không tìm thấy dữ liệu.",
        409: "Trùng dữ liệu hoặc còn quan hệ phụ thuộc.",
        503: "Database hoặc dịch vụ tạm thời không khả dụng.",
    }

    def operation(
        tag,
        summary,
        output,
        status=200,
        body=None,
        errors=(),
        public=False,
    ):
        responses = {
            str(status): response(
                "Thành công.",
                output,
            ),
        }

        for error in errors:
            responses[str(error)] = response(
                error_names[error],
                ref("Error"),
            )

        result = {
            "tags": [tag],
            "summary": summary,
            "responses": responses,
        }

        if public:
            result["security"] = []

        if body:
            result["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": ref(body),
                    }
                },
            }

        return result

    # ------------------------------------------------------------------
    # Core API paths
    # ------------------------------------------------------------------

    paths = {
        "/health": {
            "get": operation(
                "Health",
                "Kiểm tra hoạt động",
                ref("Health"),
                public=True,
            )
        },

        "/auth/login": {
            "post": operation(
                "Auth",
                "Đăng nhập và nhận JWT",
                ref("LoginResult"),
                body="LoginInput",
                errors=(400, 401),
                public=True,
            )
        },

        "/auth/me": {
            "get": operation(
                "Auth",
                "Thông tin tài khoản hiện tại",
                ref("CurrentUser"),
                errors=(401, 403),
            )
        },

        "/users": {
            "get": operation(
                "Users",
                "Danh sách tài khoản — Administrator",
                array("Account"),
                errors=(401, 403),
            ),
            "post": operation(
                "Users",
                "Tạo tài khoản — Administrator",
                ref("Account"),
                status=201,
                body="CreateAccount",
                errors=(400, 401, 403, 409),
            ),
        },

        "/users/{id}/role": {
            "parameters": [{
                "name": "id",
                "in": "path",
                "required": True,
                "schema": uuid,
            }],
            "patch": operation(
                "Users",
                "Đổi vai trò — Administrator",
                ref("Account"),
                body="ChangeRole",
                errors=(400, 401, 403, 404),
            ),
        },

        "/assets": {
            "get": operation(
                "Assets",
                "Cây tài sản — cả ba vai trò",
                array("Node"),
                errors=(401, 403),
            )
        },
    }

    # ------------------------------------------------------------------
    # Alert API
    # ------------------------------------------------------------------

    alert_filters = [
        {
            "name": "node_id",
            "in": "query",
            "required": False,
            "description": "Lọc theo UUID của Node.",
            "schema": uuid,
        },
        {
            "name": "metric",
            "in": "query",
            "required": False,
            "description": "Lọc theo chỉ số giám sát.",
            "schema": {
                "type": "string",
                "enum": [
                    "cpu_percent",
                    "memory_percent",
                    "disk_percent",
                    "node_offline_seconds",
                ],
            },
        },
        {
            "name": "severity",
            "in": "query",
            "required": False,
            "description": "Lọc theo mức độ nghiêm trọng.",
            "schema": {
                "type": "string",
                "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            },
        },
        {
            "name": "status",
            "in": "query",
            "required": False,
            "description": "Lọc theo trạng thái Alert.",
            "schema": {
                "type": "string",
                "enum": ["FIRING", "ACKNOWLEDGED", "RECOVERED"],
            },
        },
        {
            "name": "start_time",
            "in": "query",
            "required": False,
            "description": "Lọc Alert được kích hoạt từ thời điểm này.",
            "schema": {
                "type": "string",
                "format": "date-time",
            },
        },
        {
            "name": "end_time",
            "in": "query",
            "required": False,
            "description": "Lọc Alert được kích hoạt đến thời điểm này.",
            "schema": {
                "type": "string",
                "format": "date-time",
            },
        },
        {
            "name": "page",
            "in": "query",
            "required": False,
            "description": "Trang kết quả, bắt đầu từ 1.",
            "schema": {
                "type": "integer",
                "minimum": 1,
                "default": 1,
            },
        },
        {
            "name": "page_size",
            "in": "query",
            "required": False,
            "description": "Số Alert tối đa trên một trang.",
            "schema": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 20,
            },
        },
    ]

    paths["/alerts"] = {
        "get": {
            **operation(
                "Alerts",
                "Danh sách Alert — cả ba vai trò",
                ref("AlertList"),
                errors=(400, 401, 403, 503),
            ),
            "description": (
                "Tra cứu Alert theo Node, metric, severity, status "
                "và khoảng thời gian kích hoạt. Kết quả được phân trang."
            ),
            "parameters": alert_filters,
        },
    }

    paths["/alerts/{alert_id}"] = {
        "parameters": [{
            "name": "alert_id",
            "in": "path",
            "required": True,
            "description": "UUID của Alert.",
            "schema": uuid,
        }],
        "get": operation(
            "Alerts",
            "Chi tiết Alert — cả ba vai trò",
            ref("Alert"),
            errors=(400, 401, 403, 404, 503),
        ),
    }

    paths["/alerts/{alert_id}/acknowledge"] = {
        "parameters": [{
            "name": "alert_id",
            "in": "path",
            "required": True,
            "description": "UUID của Alert cần xác nhận.",
            "schema": uuid,
        }],
        "post": {
            **operation(
                "Alerts",
                "Xác nhận Alert — Administrator, Operator",
                ref("Alert"),
                errors=(400, 401, 403, 404, 409, 503),
            ),
            "description": (
                "Xác nhận Alert đang ở trạng thái FIRING. "
                "Người xác nhận được lấy từ tài khoản trong JWT hiện tại; "
                "client không gửi actor_id hoặc request body. "
                "Thao tác chuyển FIRING thành ACKNOWLEDGED, "
                "ghi acknowledged_by và acknowledged_at. "
                "ACKNOWLEDGED không đồng nghĩa với RECOVERED. "
                "Nếu Alert đã ACKNOWLEDGED, yêu cầu lặp lại trả về "
                "trạng thái hiện tại mà không tạo lịch sử xác nhận trùng. "
                "Alert đã RECOVERED không thể được xác nhận."
            ),
        },
    }

    # ------------------------------------------------------------------
    # Marker API - Task 58
    # ------------------------------------------------------------------

    paths["/markers"] = {
        "get": operation(
            "Markers",
            "Danh sách Marker — Administrator",
            array("Marker"),
            errors=(401, 403),
        ),

        "post": operation(
            "Markers",
            "Đăng ký Marker — Administrator",
            ref("Marker"),
            status=201,
            body="CreateMarker",
            errors=(400, 401, 403, 409),
        ),
    }

    paths["/markers/lookup"] = {
        "get": {
            "tags": ["Markers"],
            "summary": "Tra cứu Node từ Marker — cả ba vai trò",
            "parameters": [
                {
                    "name": "marker_type",
                    "in": "query",
                    "required": True,
                    "schema": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 32,
                        "pattern": r"\S",
                    },
                },
                {
                    "name": "identifier",
                    "in": "query",
                    "required": True,
                    "schema": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 128,
                        "pattern": r"\S",
                    },
                },
            ],
            "responses": {
                "200": response(
                    "Marker và Node tương ứng.",
                    ref("MarkerLookupResult"),
                ),
                "401": response(
                    error_names[401],
                    ref("Error"),
                ),
                "403": response(
                    error_names[403],
                    ref("Error"),
                ),
                "404": response(
                    "Marker không tồn tại hoặc đã bị vô hiệu hóa.",
                    ref("Error"),
                ),
            },
        }
    }

    paths["/markers/{marker_id}/deactivate"] = {
        "parameters": [{
            "name": "marker_id",
            "in": "path",
            "required": True,
            "schema": uuid,
        }],
        "patch": operation(
            "Markers",
            "Vô hiệu hóa Marker — Administrator",
            ref("Marker"),
            errors=(401, 403, 404),
        ),
    }

    # ------------------------------------------------------------------
    # Telemetry Query API
    # ------------------------------------------------------------------

    paths["/telemetry/nodes/{node_id}/latest"] = {
        "parameters": [{
            "name": "node_id",
            "in": "path",
            "required": True,
            "description": "UUID của Node cần truy vấn.",
            "schema": uuid,
        }],
        "get": operation(
            "Telemetry",
            "Lấy dữ liệu Telemetry mới nhất của Node",
            ref("TelemetryLatest"),
            errors=(400, 401, 403, 404, 503),
        ),
    }

    paths["/telemetry/nodes/{node_id}/history"] = {
        "parameters": [{
            "name": "node_id",
            "in": "path",
            "required": True,
            "description": "UUID của Node cần truy vấn.",
            "schema": uuid,
        }],
        "get": {
            **operation(
                "Telemetry",
                "Lấy lịch sử Telemetry của Node",
                ref("TelemetryHistory"),
                errors=(400, 401, 403, 404, 503),
            ),
            "description": (
                "Lọc theo measured_at trong khoảng [start, end). "
                "Kết quả sắp xếp tăng dần theo measured_at, "
                "received_at và id. "
                "Múi giờ của start và end là bắt buộc."
            ),
            "parameters": [
                {
                    "name": "start",
                    "in": "query",
                    "required": True,
                    "description": (
                        "Thời điểm bắt đầu, được tính vào kết quả. "
                        "Phải là ISO 8601 có múi giờ."
                    ),
                    "schema": {
                        "type": "string",
                        "format": "date-time",
                    },
                    "example": "2026-11-24T00:00:00Z",
                },
                {
                    "name": "end",
                    "in": "query",
                    "required": True,
                    "description": (
                        "Thời điểm kết thúc, không được tính vào "
                        "kết quả. Phải lớn hơn start."
                    ),
                    "schema": {
                        "type": "string",
                        "format": "date-time",
                    },
                    "example": "2026-11-25T00:00:00Z",
                },
                {
                    "name": "limit",
                    "in": "query",
                    "required": False,
                    "description": "Số bản ghi tối đa cần trả về.",
                    "schema": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 1000,
                        "default": 1000,
                    },
                },
            ],
        },
    }

    # ------------------------------------------------------------------
    # Telemetry examples
    # ------------------------------------------------------------------

    paths["/telemetry/nodes/{node_id}/latest"]["get"]["responses"][
        "200"
    ]["content"]["application/json"]["example"] = {
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
            "disk_percent": 72.0,
        },
        "monitoring": {
            "connection_status": "online",
            "data_status": "fresh",
            "last_received_at": "2026-11-24T07:59:56+00:00",
            "last_measured_at": "2026-11-24T07:59:55+00:00",
            "seconds_since_received": 4,
            "seconds_since_measured": 5,
            "stale_after_seconds": 30,
            "offline_after_seconds": 90,
        },
        "poll_interval_seconds": 5,
    }

    paths["/telemetry/nodes/{node_id}/history"]["get"]["responses"][
        "200"
    ]["content"]["application/json"]["example"] = {
        "node_id": "0fa96124-f0ab-4cb6-8919-8fcd4c8c6fad",
        "start": "2026-11-24T00:00:00+00:00",
        "end": "2026-11-25T00:00:00+00:00",
        "limit": 100,
        "count": 1,
        "limit_reached": False,
        "items": [
            {
                "id": "6d2c3b31-6eaf-45e7-bd5a-2c5e3aaf43d0",
                "message_id": "c2e50e44-f789-4e1c-a8f4-abc123456789",
                "node_id": "0fa96124-f0ab-4cb6-8919-8fcd4c8c6fad",
                "measured_at": "2026-11-24T07:59:55+00:00",
                "received_at": "2026-11-24T07:59:56+00:00",
                "cpu_percent": 45.5,
                "memory_percent": 68.2,
                "disk_percent": 72.0,
            }
        ],
    }

    # ------------------------------------------------------------------
    # Telemetry Agent Ingestion API
    # ------------------------------------------------------------------

    paths["/telemetry"] = {
        "post": {
            "tags": ["Telemetry"],
            "summary": "Agent gửi dữ liệu Telemetry cho Node",
            "description": (
                "Agent phải xác thực bằng TLS client certificate. "
                "Backend kiểm tra SHA-256 fingerprint của chứng chỉ "
                "với Agent Registry và kiểm tra quyền truy cập Node. "
                "Không sử dụng Bearer JWT hoặc X-Agent-Key cho endpoint "
                "này. Gửi lại cùng message_id và payload sẽ không tạo "
                "bản ghi trùng. Nếu message_id trùng nhưng payload "
                "khác, trả về 409."
            ),
            "security": [],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": ref("TelemetryInput"),
                    }
                },
            },
            "responses": {
                "200": response(
                    "Đã tiếp nhận hoặc bản tin đã tồn tại.",
                    ref("TelemetryRecord"),
                ),
                "400": response(
                    "Dữ liệu không hợp lệ.",
                    ref("Error"),
                ),
                "401": response(
                    "Thiếu hoặc không hợp lệ TLS client certificate.",
                    ref("Error"),
                ),
                "403": response(
                    "Agent không có quyền gửi cho Node.",
                    ref("Error"),
                ),
                "409": response(
                    "message_id đã tồn tại với payload khác.",
                    ref("Error"),
                ),
                "503": response(
                    "Database hoặc Agent Registry tạm thời không khả dụng.",
                    ref("Error"),
                ),
                "500": response(
                    "Lỗi hệ thống.",
                    ref("Error"),
                ),
            },
        }
    }

    # ------------------------------------------------------------------
    # CRUD resource API paths
    # ------------------------------------------------------------------

    for path, model, detail, properties, required in resources:
        create_name = f"Create_{path}"
        update_name = f"Update_{path}"

        schemas[create_name] = input_schema(
            properties,
            required,
        )

        schemas[update_name] = input_schema(
            properties,
            [],
        )

        schemas[update_name]["minProperties"] = 1

        paths[f"/{path}"] = {
            "get": operation(
                path,
                "Danh sách — cả ba vai trò",
                array(model),
                errors=(401, 403),
            ),
            "post": operation(
                path,
                "Tạo — Administrator, Operator",
                ref(model),
                status=201,
                body=create_name,
                errors=(400, 401, 403, 409),
            ),
        }

        paths[f"/{path}/{{id}}"] = {
            "parameters": [{
                "name": "id",
                "in": "path",
                "required": True,
                "schema": uuid,
            }],
            "get": operation(
                path,
                "Chi tiết — cả ba vai trò",
                ref(detail),
                errors=(400, 401, 403, 404),
            ),
            "patch": operation(
                path,
                "Cập nhật — Administrator, Operator",
                ref(model),
                body=update_name,
                errors=(400, 401, 403, 404, 409),
            ),
            "delete": operation(
                path,
                "Xóa — Administrator",
                ref("Message"),
                errors=(400, 401, 403, 404, 409),
            ),
        }

    # ------------------------------------------------------------------
    # Return OpenAPI document
    # ------------------------------------------------------------------

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "AR-IMMS Backend Python",
            "version": "1.0.0",
            "description": (
                "API lõi Flask. Các API dành cho Web Portal yêu cầu "
                "Bearer JWT. Endpoint POST /telemetry dành cho Agent "
                "sử dụng TLS client certificate (mTLS). "
                "Code và name được loại bỏ khoảng trắng đầu/cuối "
                "trước khi kiểm tra. Các trường không có trong schema "
                "tạo/cập nhật tài sản sẽ bị từ chối."
            ),
        },
        "servers": [{"url": "/"}],
        "security": [{"bearerAuth": []}],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                },
            },
            "schemas": schemas,
        },
    }
