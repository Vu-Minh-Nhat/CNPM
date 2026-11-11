from datetime import datetime

from flask import Blueprint, jsonify, request

from src.api.middleware import require_auth
from src.domain.constants import Role
from src.services.session_service import SessionService
from src.services.telemetry_service import TelemetryService


def create_telemetry_blueprint(
    telemetry_service: TelemetryService,
    session_service: SessionService,
):
    blueprint = Blueprint(
        "telemetry",
        __name__,
        url_prefix="/telemetry",
    )

    @blueprint.post("")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def ingest_telemetry():
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "message": "Dữ liệu telemetry không hợp lệ.",
                "error": "BadRequest",
                "statusCode": 400,
            }), 400

        required_fields = [
            "message_id",
            "node_id",
            "measured_at",
            "cpu_percent",
            "memory_percent",
            "disk_percent",
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in data
        ]

        if missing_fields:
            return jsonify({
                "message": (
                    "Thiếu trường bắt buộc: "
                    + ", ".join(missing_fields)
                ),
                "error": "BadRequest",
                "statusCode": 400,
            }), 400

        try:
            measured_at = datetime.fromisoformat(
                str(data["measured_at"]).replace("Z", "+00:00")
            )

            cpu_percent = float(data["cpu_percent"])
            memory_percent = float(data["memory_percent"])
            disk_percent = float(data["disk_percent"])
        except (TypeError, ValueError):
            return jsonify({
                "message": "Dữ liệu telemetry không đúng định dạng.",
                "error": "BadRequest",
                "statusCode": 400,
            }), 400

        percentages = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent": disk_percent,
        }

        invalid_percentages = [
            field
            for field, value in percentages.items()
            if value < 0 or value > 100
        ]

        if invalid_percentages:
            return jsonify({
                "message": (
                    "Giá trị phần trăm phải nằm trong khoảng 0 đến 100: "
                    + ", ".join(invalid_percentages)
                ),
                "error": "BadRequest",
                "statusCode": 400,
            }), 400

        try:
            record = telemetry_service.ingest(
                message_id=str(data["message_id"]),
                node_id=str(data["node_id"]),
                measured_at=measured_at,
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
            )
        except Exception:
            return jsonify({
                "message": "Không thể lưu dữ liệu telemetry.",
                "error": "InternalServerError",
                "statusCode": 500,
            }), 500

        return jsonify({
            "id": record.id,
            "message_id": record.message_id,
            "node_id": record.node_id,
            "measured_at": record.measured_at.isoformat(),
            "cpu_percent": record.cpu_percent,
            "memory_percent": record.memory_percent,
            "disk_percent": record.disk_percent,
            "received_at": record.received_at.isoformat(),
        }), 200

    return blueprint