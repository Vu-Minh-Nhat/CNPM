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

    schemas["Health"] = object_schema({
        "status": {"type": "string", "example": "ok"},
        "service": {"type": "string", "example": "ar-imms-backend"},
        "timestamp": {"type": "string", "format": "date-time"},
        "uptimeSeconds": {"type": "integer", "minimum": 0},
    })

    schemas["LoginInput"] = object_schema({
        "email": {"type": "string", "example": "admin@arimms.local"},
        "password": {"type": "string", "format": "password"},
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
        "email": {"type": "string", "format": "email", "maxLength": 254},
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

    site_fields = {"id": uuid, "code": code, "name": name}
    room_fields = {
        "id": uuid, "siteId": uuid, "code": code, "name": name,
    }
    rack_fields = {
        "id": uuid,
        "roomId": uuid,
        "code": code,
        "name": name,
        "capacityU": {"type": "integer", "minimum": 1, "maximum": 100},
    }
    node_fields = {
        "id": uuid,
        "rackId": uuid,
        "code": code,
        "name": name,
        "serialNumber": {
            "type": "string", "maxLength": 128, "nullable": True,
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
            "type": "string", "maxLength": 200, "nullable": True,
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

    resources = (
        ("sites", "Site", "Site", {"code": code, "name": name},
         ["code", "name"]),
        ("rooms", "Room", "RoomDetail",
         {"siteId": uuid, "code": code, "name": name},
         ["siteId", "code", "name"]),
        ("racks", "Rack", "RackDetail",
         {
             "roomId": uuid,
             "code": code,
             "name": name,
             "capacityU": {
                 "type": "integer", "minimum": 1, "maximum": 100,
             },
         },
         ["roomId", "code", "name", "capacityU"]),
        ("servers", "Node", "Node",
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
         ["rackId", "code", "name"]),
    )

    def response(description, schema):
        return {
            "description": description,
            "content": {"application/json": {"schema": schema}},
        }

    error_names = {
        400: "Dữ liệu không hợp lệ.",
        401: "Chưa xác thực hoặc token không hợp lệ.",
        403: "Không đủ quyền.",
        404: "Không tìm thấy dữ liệu.",
        409: "Trùng dữ liệu hoặc còn quan hệ phụ thuộc.",
    }

    def operation(
        tag, summary, output, status=200,
        body=None, errors=(), public=False,
    ):
        responses = {
            str(status): response("Thành công.", output),
        }

        for error in errors:
            responses[str(error)] = response(
                error_names[error], ref("Error")
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
                    "application/json": {"schema": ref(body)}
                },
            }

        return result

    paths = {
        "/health": {
            "get": operation(
                "Health", "Kiểm tra hoạt động",
                ref("Health"), public=True,
            )
        },
        "/auth/login": {
            "post": operation(
                "Auth", "Đăng nhập và nhận JWT",
                ref("LoginResult"),
                body="LoginInput",
                errors=(400, 401),
                public=True,
            )
        },
        "/auth/me": {
            "get": operation(
                "Auth", "Thông tin tài khoản hiện tại",
                ref("CurrentUser"), errors=(401, 403),
            )
        },
        "/users": {
            "get": operation(
                "Users", "Danh sách tài khoản — Administrator",
                array("Account"), errors=(401, 403),
            ),
            "post": operation(
                "Users", "Tạo tài khoản — Administrator",
                ref("Account"), status=201,
                body="CreateAccount", errors=(400, 401, 403, 409),
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
                "Users", "Đổi vai trò — Administrator",
                ref("Account"), body="ChangeRole",
                errors=(400, 401, 403, 404),
            ),
        },
        "/assets": {
            "get": operation(
                "Assets", "Cây tài sản — cả ba vai trò",
                array("Node"), errors=(401, 403),
            )
        },
    }

    for path, model, detail, properties, required in resources:
        create_name = f"Create_{path}"
        update_name = f"Update_{path}"

        schemas[create_name] = input_schema(properties, required)
        schemas[update_name] = input_schema(properties, [])
        schemas[update_name]["minProperties"] = 1

        paths[f"/{path}"] = {
            "get": operation(
                path, "Danh sách — cả ba vai trò",
                array(model), errors=(401, 403),
            ),
            "post": operation(
                path, "Tạo — Administrator, Operator",
                ref(model), status=201, body=create_name,
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
                path, "Chi tiết — cả ba vai trò",
                ref(detail), errors=(400, 401, 403, 404),
            ),
            "patch": operation(
                path, "Cập nhật — Administrator, Operator",
                ref(model), body=update_name,
                errors=(400, 401, 403, 404, 409),
            ),
            "delete": operation(
                path, "Xóa — Administrator",
                ref("Message"), errors=(400, 401, 403, 404, 409),
            ),
        }

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "AR-IMMS Backend Python",
            "version": "1.0.0",
            "description": (
                "API lõi Flask. Các API có khóa yêu cầu Bearer JWT. "
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
                }
            },
            "schemas": schemas,
        },
    }