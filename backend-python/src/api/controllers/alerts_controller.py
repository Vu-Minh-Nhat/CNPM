
from datetime import datetime

from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from src.api.middleware import require_auth
from src.domain.constants import Role
from src.domain.exceptions import ValidationError
from src.services.alert_service import AlertService
from src.services.session_service import SessionService


def create_alerts_blueprint(
    alert_service: AlertService,
    session_service: SessionService,
) -> Blueprint:
    blueprint = Blueprint(
        "alerts",
        __name__,
        url_prefix="/alerts",
    )

    @blueprint.errorhandler(SQLAlchemyError)
    def database_error(error):
        return jsonify({
            "message": "Không thể truy vấn cảnh báo lúc này.",
            "error": "Service Unavailable",
            "statusCode": 503,
        }), 503

    def parse_optional_time(name: str) -> datetime | None:
        value = request.args.get(name)

        if value is None or not value.strip():
            return None

        try:
            parsed = datetime.fromisoformat(
                value.strip().replace("Z", "+00:00")
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

    def parse_integer(name: str, default: int) -> int:
        value = request.args.get(name)

        if value is None:
            return default

        try:
            return int(value)
        except (TypeError, ValueError) as error:
            raise ValidationError(
                f"{name} phải là số nguyên."
            ) from error

    @blueprint.get("")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def list_alerts():
        node_id = request.args.get("node_id")
        metric = request.args.get("metric")
        severity = request.args.get("severity")
        status = request.args.get("status")

        start_time = parse_optional_time("start_time")
        end_time = parse_optional_time("end_time")

        if (
            start_time is not None
            and end_time is not None
            and start_time >= end_time
        ):
            raise ValidationError(
                "end_time phải lớn hơn start_time."
            )

        page = parse_integer("page", 1)
        page_size = parse_integer("page_size", 20)

        result = alert_service.list_alerts(
            node_id=node_id,
            metric=metric,
            severity=severity,
            status=status,
            start_time=start_time,
            end_time=end_time,
            page=page,
            page_size=page_size,
        )

        return jsonify(result), 200

    @blueprint.get("/<alert_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def get_alert(alert_id):
        result = alert_service.get_alert(alert_id)

        return jsonify(result), 200

    @blueprint.post("/<alert_id>/acknowledge")
    @require_auth(
        session_service=session_service,
        allowed_roles=(
            Role.ADMINISTRATOR,
            Role.OPERATOR,
        ),
    )
    def acknowledge_alert(alert_id):
        result = alert_service.acknowledge_alert(
            alert_id=alert_id,
            actor_id=str(g.current_account.id),
        )

        return jsonify(result), 200

    return blueprint
