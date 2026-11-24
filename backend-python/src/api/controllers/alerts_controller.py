from __future__ import annotations

import os
from typing import Any, Dict

from flask import Blueprint, current_app, jsonify, request

from src.services.alert_query_ack_service import AlertApiError, AlertQueryAckService

alerts_bp = Blueprint("alerts", __name__, url_prefix="/alerts")


def _require_auth_flag() -> bool:
    raw = os.environ.get("ALERT_API_REQUIRE_AUTH", "false").strip().lower()
    return raw in ("1", "true", "yes")


def _get_service() -> AlertQueryAckService:
    svc = current_app.extensions.get("alert_query_ack_service")
    if svc is None:
        raise AlertApiError(500, "ALERT_SERVICE_UNAVAILABLE", "Alert query/ack service is not initialized")
    return svc


@alerts_bp.errorhandler(AlertApiError)
def handle_alert_api_error(err: AlertApiError):
    return jsonify({"error": err.code, "message": err.message}), err.status_code


@alerts_bp.get("")
def list_alerts_endpoint():
    svc = _get_service()
    svc.ensure_read_permission(dict(request.headers), require_auth=_require_auth_flag())
    result = svc.list_alerts(request.args.to_dict(flat=True))
    return jsonify(result), 200


@alerts_bp.get("/<string:alert_id>")
def get_alert_detail_endpoint(alert_id: str):
    svc = _get_service()
    svc.ensure_read_permission(dict(request.headers), require_auth=_require_auth_flag())
    detail = svc.get_alert_detail(alert_id)
    return jsonify(detail), 200


@alerts_bp.post("/<string:alert_id>/acknowledge")
def acknowledge_alert_endpoint(alert_id: str):
    svc = _get_service()
    body: Dict[str, Any] = request.get_json(silent=True) or {}
    result = svc.acknowledge_alert(
        alert_id=alert_id,
        headers=dict(request.headers),
        body=body,
        require_auth=_require_auth_flag(),
    )
    return jsonify(result), 200