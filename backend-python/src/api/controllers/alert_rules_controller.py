from flask import Blueprint, jsonify, request
from src.services.alert_detector_service import AlertRule

alert_rules_bp = Blueprint("alert_rules", __name__, url_prefix="/alert-rules")


def register_alert_rule_routes(app, rule_manager, detector=None):
    @alert_rules_bp.get("")
    def list_rules():
        return jsonify({"items": [r.__dict__ for r in rule_manager.list_rules()]}), 200

    @alert_rules_bp.post("")
    def create_or_update_rule():
        role = request.headers.get("X-User-Role", "viewer")
        data = request.get_json(silent=True) or {}
        try:
            rule = AlertRule(
                id=str(data["id"]),
                name=str(data["name"]),
                metric=str(data["metric"]),
                threshold=float(data["threshold"]),
                recovery_threshold=float(data["recovery_threshold"]),
                enabled=bool(data.get("enabled", True)),
                stale_after_seconds=int(data.get("stale_after_seconds", 30)),
                offline_after_seconds=int(data.get("offline_after_seconds", 90)),
            )
            saved = rule_manager.upsert_rule(rule, actor_role=role)
            return jsonify(saved.__dict__), 200
        except PermissionError as exc:
            return jsonify({"error": str(exc)}), 403
        except (KeyError, TypeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

    @alert_rules_bp.patch("/<rule_id>/toggle")
    def toggle_rule(rule_id: str):
        role = request.headers.get("X-User-Role", "viewer")
        data = request.get_json(silent=True) or {}
        if "enabled" not in data:
            return jsonify({"error": "Missing 'enabled' boolean"}), 400
        try:
            updated = rule_manager.set_enabled(rule_id, bool(data["enabled"]), actor_role=role)
            return jsonify(updated.__dict__), 200
        except PermissionError as exc:
            return jsonify({"error": str(exc)}), 403
        except KeyError as exc:
            return jsonify({"error": str(exc)}), 404

    if detector is not None:
        @alert_rules_bp.get("/alerts")
        def list_alerts():
            items = []
            for alert in detector._alerts.values():
                d = alert.__dict__.copy()
                for k, v in list(d.items()):
                    if hasattr(v, "isoformat"):
                        d[k] = v.isoformat()
                items.append(d)
            return jsonify({"items": items}), 200

    app.register_blueprint(alert_rules_bp)