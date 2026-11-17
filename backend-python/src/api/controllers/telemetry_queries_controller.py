from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from src.api.middleware import require_auth
from src.domain.constants import Role
from src.domain.exceptions import ValidationError
from src.services.session_service import SessionService
from src.services.telemetry_query_service import TelemetryQueryService


def create_telemetry_queries_blueprint(
    query_service: TelemetryQueryService,
    session_service: SessionService,
) -> Blueprint:
    blueprint = Blueprint(
        "telemetry_queries",
        __name__,
        url_prefix="/telemetry/nodes",
    )

    @blueprint.errorhandler(SQLAlchemyError)
    def database_error(error):
        return jsonify({
            "message": "Không thể đọc dữ liệu giám sát lúc này.",
            "error": "Service Unavailable",
            "statusCode": 503,
        }), 503

    def parse_time(name: str) -> datetime:
        value = request.args.get(name)

        if not value:
            raise ValidationError(
                f"Cần cung cấp tham số {name}."
            )

        try:
            parsed = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError as error:
            raise ValidationError(
                f"{name} phải là timestamp ISO 8601 hợp lệ."
            ) from error

        if parsed.utcoffset() is None:
            raise ValidationError(
                f"{name} phải có múi giờ."
            )

        return parsed

    @blueprint.get("/<node_id>/latest")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def latest(node_id):
        return jsonify(query_service.get_latest(node_id)), 200

    @blueprint.get("/<node_id>/history")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def history(node_id):
        start = parse_time("start")
        end = parse_time("end")

        try:
            limit = int(request.args.get("limit", "1000"))
        except ValueError as error:
            raise ValidationError(
                "limit phải là số nguyên."
            ) from error

        result = query_service.get_history(
            node_id,
            start=start,
            end=end,
            limit=limit,
        )

        return jsonify(result), 200

    return blueprint