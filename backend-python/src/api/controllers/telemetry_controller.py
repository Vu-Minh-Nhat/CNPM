
import hmac
import os
from datetime import datetime, timezone
from math import isfinite

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from src.domain.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)
from src.services.session_service import SessionService
from src.services.telemetry_service import TelemetryService


def create_telemetry_blueprint(
    telemetry_service: TelemetryService,
    session_service: SessionService,
):
    blueprint = Blueprint("telemetry", __name__, url_prefix="/telemetry")

    @blueprint.post("")
    def ingest_telemetry():
        # 1. Authenticate Agent
        configured_key = os.getenv("TELEMETRY_AGENT_KEY", "").strip()
        provided_key = request.headers.get("X-Agent-Key", "")

        if not configured_key:
            return jsonify({
                "message": "Server chua cau hinh Agent API key.",
                "error": "ServiceUnavailable",
                "statusCode": 503,
            }), 503

        if not provided_key or not hmac.compare_digest(
            provided_key, configured_key
        ):
            return jsonify({
                "message": "Agent API key khong hop le.",
                "error": "Unauthorized",
                "statusCode": 401,
            }), 401

        # 2. Validate request body
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "message": "Du lieu telemetry khong hop le.",
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
            field for field in required_fields if field not in data
        ]

        if missing_fields:
            return jsonify({
                "message": "Thieu truong bat buoc.",
                "missingFields": missing_fields,
                "error": "BadRequest",
                "statusCode": 400,
            }), 400

        # 3. Check Agent permission for Node
        allowed_node_ids = {
            item.strip()
            for item in os.getenv(
                "TELEMETRY_AGENT_NODE_IDS", ""
            ).split(",")
            if item.strip()
        }

        node_id = str(data["node_id"])

        if node_id not in allowed_node_ids:
            return jsonify({
                "message": "Agent khong co quyen gui du lieu cho Node nay.",
                "error": "Forbidden",
                "statusCode": 403,
            }), 403

        # 4. Validate timestamp and metric values
        try:
            measured_at = datetime.fromisoformat(
                str(data["measured_at"]).replace("Z", "+00:00")
            )

            if measured_at.tzinfo is None:
                raise ValueError("Timestamp phai co mui gio.")

            percentages = {}

            for field in (
                "cpu_percent",
                "memory_percent",
                "disk_percent",
            ):
                value = data[field]

                if isinstance(value, bool):
                    raise ValueError(f"{field} khong hop le.")

                value = float(value)

                if not isfinite(value) or not 0 <= value <= 100:
                    raise ValueError(
                        f"{field} phai nam trong khoang 0 den 100."
                    )

                percentages[field] = value

        except (TypeError, ValueError, OverflowError):
            return jsonify({
                "message": "Timestamp hoac gia tri telemetry khong hop le.",
                "error": "BadRequest",
                "statusCode": 400,
            }), 400

        # 5. Save telemetry
        try:
            record = telemetry_service.ingest(
                message_id=str(data["message_id"]),
                node_id=node_id,
                measured_at=measured_at.astimezone(timezone.utc),
                cpu_percent=percentages["cpu_percent"],
                memory_percent=percentages["memory_percent"],
                disk_percent=percentages["disk_percent"],
            )

        except ResourceConflictError as exc:
            return jsonify({
                "message": str(exc),
                "error": "Conflict",
                "statusCode": 409,
            }), 409

        except ValidationError as exc:
            return jsonify({
                "message": str(exc),
                "error": "BadRequest",
                "statusCode": 400,
            }), 400

        except ResourceNotFoundError as exc:
            return jsonify({
                "message": str(exc),
                "error": "NotFound",
                "statusCode": 404,
            }), 404

        except SQLAlchemyError:
            return jsonify({
                "message": "Database tam thoi khong kha dung.",
                "error": "ServiceUnavailable",
                "statusCode": 503,
            }), 503

        except Exception:
            return jsonify({
                "message": "Loi he thong khi xu ly telemetry.",
                "error": "InternalServerError",
                "statusCode": 500,
            }), 500

        # 6. Return saved record
        return jsonify({
            "id": str(record.id),
            "message_id": str(record.message_id),
            "node_id": str(record.node_id),
            "measured_at": record.measured_at.isoformat(),
            "cpu_percent": record.cpu_percent,
            "memory_percent": record.memory_percent,
            "disk_percent": record.disk_percent,
            "received_at": record.received_at.isoformat(),
        }), 200

    return blueprint
