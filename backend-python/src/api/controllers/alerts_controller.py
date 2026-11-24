from flask import Blueprint, jsonify

from src.api.middleware import require_auth
from src.domain.constants import Role
from src.services.alert_service import AlertService
from src.services.session_service import SessionService


def create_alerts_blueprint(
    alert_service: AlertService,
    session_service: SessionService,
) -> Blueprint:
    blueprint = Blueprint("alerts", __name__, url_prefix="/alerts")

    @blueprint.get("")
    @require_auth(
        session_service=session_service,
        allowed_roles=(
            Role.ADMINISTRATOR,
            Role.OPERATOR,
            Role.TECHNICIAN,
        ),
    )
    def list_alerts():
        return jsonify(alert_service.list_alerts()), 200

    @blueprint.patch("/<alert_id>/acknowledge")
    @require_auth(
        session_service=session_service,
        allowed_roles=(
            Role.ADMINISTRATOR,
            Role.OPERATOR,
            Role.TECHNICIAN,
        ),
    )
    def acknowledge_alert(alert_id):
        return jsonify(alert_service.acknowledge(alert_id)), 200

    return blueprint