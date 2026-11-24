from __future__ import annotations

from typing import Any, Dict, Optional

from flask import Blueprint, jsonify

openapi_bp = Blueprint("openapi", __name__)


ALERT_SCHEMAS: Dict[str, Any] = {
    "AuditLogEntry": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "alert_created",
                    "alert_updated",
                    "alert_acknowledged",
                    "alert_resolved",
                ],
            },
            "actor": {"type": "string", "example": "op-khoi"},
            "role": {"type": "string", "nullable": True, "example": "operator"},
            "timestamp": {"type": "string", "format": "date-time"},
            "detail": {"type": "object", "additionalProperties": True},
        },
        "required": ["action", "actor", "timestamp"],
    },
    "AlertItem": {
        "type": "object",
        "properties": {
            "alert_id": {"type": "string", "example": "ALT-000001"},
            "rule_id": {"type": "string", "nullable": True, "example": "rule-cpu-high"},
            "node_id": {"type": "string", "example": "node-01"},
            "alert_type": {
                "type": "string",
                "enum": ["threshold", "node_offline"],
                "example": "threshold",
            },
            "severity": {
                "type": "string",
                "enum": ["warning", "critical"],
                "example": "critical",
            },
            "status": {
                "type": "string",
                "enum": ["active", "resolved"],
                "example": "active",
            },
            "reason": {
                "type": "string",
                "example": "cpu value 88.0 exceeded threshold 70.0",
            },
            "value": {"type": "number", "format": "float", "nullable": True, "example": 88.0},
            "threshold": {"type": "number", "format": "float", "nullable": True, "example": 70.0},
            "hit_count": {"type": "integer", "example": 1},
            "created_at": {"type": "string", "format": "date-time", "nullable": True},
            "updated_at": {"type": "string", "format": "date-time", "nullable": True},
            "resolved_at": {"type": "string", "format": "date-time", "nullable": True},
            "resolution_reason": {"type": "string", "nullable": True, "example": "rule_disabled"},
            "acknowledged": {"type": "boolean", "example": False},
            "acknowledged_by": {"type": "string", "nullable": True, "example": None},
            "acknowledged_at": {"type": "string", "format": "date-time", "nullable": True},
        },
        "required": [
            "alert_id",
            "node_id",
            "alert_type",
            "severity",
            "status",
            "reason",
            "hit_count",
            "acknowledged",
        ],
    },
    "AlertDetail": {
        "allOf": [
            {"$ref": "#/components/schemas/AlertItem"},
            {
                "type": "object",
                "properties": {
                    "audit_logs": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/AuditLogEntry"},
                    }
                },
                "required": ["audit_logs"],
            },
        ]
    },
    "AlertListResponse": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/AlertItem"},
            },
            "total": {"type": "integer", "example": 2},
            "page": {"type": "integer", "example": 1},
            "page_size": {"type": "integer", "example": 20},
            "total_pages": {"type": "integer", "example": 1},
        },
        "required": ["items", "total", "page", "page_size", "total_pages"],
    },
    "AcknowledgeAlertRequest": {
        "type": "object",
        "properties": {
            "acknowledged_by": {
                "type": "string",
                "nullable": True,
                "example": "op-khoi",
            },
            "note": {
                "type": "string",
                "nullable": True,
                "example": "Đã tiếp nhận và kiểm tra node",
            },
        },
    },
}


ALERT_PATHS: Dict[str, Any] = {
    "/alerts": {
        "get": {
            "tags": ["Alerts"],
            "summary": "Danh sách cảnh báo (hỗ trợ lọc và phân trang)",
            "description": (
                "Tra cứu cảnh báo theo node_id, loại cảnh báo, mức độ, trạng thái bất thường "
                "(active/resolved), trạng thái xác nhận (acknowledged) và khoảng thời gian."
            ),
            "parameters": [
                {
                    "name": "node_id",
                    "in": "query",
                    "schema": {"type": "string"},
                    "description": "Lọc theo mã node",
                },
                {
                    "name": "alert_type",
                    "in": "query",
                    "schema": {"type": "string", "enum": ["threshold", "node_offline"]},
                    "description": "Lọc theo loại cảnh báo",
                },
                {
                    "name": "severity",
                    "in": "query",
                    "schema": {"type": "string", "enum": ["warning", "critical"]},
                    "description": "Lọc theo mức độ cảnh báo",
                },
                {
                    "name": "status",
                    "in": "query",
                    "schema": {"type": "string", "enum": ["active", "resolved"]},
                    "description": "Lọc theo tình trạng bất thường hiện tại",
                },
                {
                    "name": "acknowledged",
                    "in": "query",
                    "schema": {"type": "boolean"},
                    "description": "Lọc theo trạng thái đã xác nhận tiếp nhận",
                },
                {
                    "name": "from",
                    "in": "query",
                    "schema": {"type": "string", "format": "date-time"},
                    "description": "Mốc thời gian bắt đầu (ISO-8601)",
                },
                {
                    "name": "to",
                    "in": "query",
                    "schema": {"type": "string", "format": "date-time"},
                    "description": "Mốc thời gian kết thúc (ISO-8601)",
                },
                {
                    "name": "page",
                    "in": "query",
                    "schema": {"type": "integer", "minimum": 1, "default": 1},
                },
                {
                    "name": "page_size",
                    "in": "query",
                    "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
                },
            ],
            "responses": {
                "200": {
                    "description": "Danh sách cảnh báo phân trang",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AlertListResponse"}
                        }
                    },
                },
                "400": {"description": "Tham số lọc hoặc phân trang không hợp lệ"},
                "401": {"description": "Chưa xác thực danh tính"},
                "403": {"description": "Không đủ quyền truy cập"},
            },
        }
    },
    "/alerts/{alert_id}": {
        "get": {
            "tags": ["Alerts"],
            "summary": "Chi tiết cảnh báo và lịch sử audit",
            "parameters": [
                {
                    "name": "alert_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "example": "ALT-000001"},
                }
            ],
            "responses": {
                "200": {
                    "description": "Chi tiết cảnh báo kèm audit_logs",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AlertDetail"}
                        }
                    },
                },
                "401": {"description": "Chưa xác thực danh tính"},
                "403": {"description": "Không đủ quyền truy cập"},
                "404": {"description": "Không tìm thấy cảnh báo"},
            },
        }
    },
    "/alerts/{alert_id}/acknowledge": {
        "post": {
            "tags": ["Alerts"],
            "summary": "Xác nhận đã tiếp nhận cảnh báo",
            "description": (
                "Ghi nhận người xác nhận và thời điểm xác nhận. Không tự động đổi status sang "
                "resolved; xử lý idempotent nếu cảnh báo đã được xác nhận trước đó."
            ),
            "parameters": [
                {
                    "name": "alert_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "example": "ALT-000001"},
                },
                {
                    "name": "X-User-Role",
                    "in": "header",
                    "schema": {"type": "string", "example": "operator"},
                },
                {
                    "name": "X-User-Id",
                    "in": "header",
                    "schema": {"type": "string", "example": "op-khoi"},
                },
            ],
            "requestBody": {
                "required": False,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/AcknowledgeAlertRequest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Đã xác nhận cảnh báo (hoặc trả lại trạng thái hiện tại nếu gọi lặp)",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AlertDetail"}
                        }
                    },
                },
                "401": {"description": "Chưa xác thực danh tính"},
                "403": {"description": "Vai trò không có quyền xác nhận cảnh báo"},
                "404": {"description": "Không tìm thấy cảnh báo"},
            },
        }
    },
}


def build_openapi_spec(existing_spec: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    spec: Dict[str, Any] = dict(existing_spec) if isinstance(existing_spec, dict) else {
        "openapi": "3.0.3",
        "info": {
            "title": "Marker Management & Telemetry Alerting API",
            "version": "1.0.0",
        },
        "paths": {},
        "components": {"schemas": {}},
    }

    paths = spec.setdefault("paths", {})
    for path, path_item in ALERT_PATHS.items():
        paths[path] = path_item

    components = spec.setdefault("components", {})
    schemas = components.setdefault("schemas", {})
    for schema_name, schema_def in ALERT_SCHEMAS.items():
        schemas[schema_name] = schema_def

    return spec


@openapi_bp.get("/openapi.json")
def get_openapi_json():
    return jsonify(build_openapi_spec()), 200