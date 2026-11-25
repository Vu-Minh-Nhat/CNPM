from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.api.middleware import require_auth
from src.domain.constants import Role
from src.infrastructure.models import AlertHistoryModel, TicketHistoryModel


def create_audit_blueprint(session_service, session_factory):
    blueprint = Blueprint("audit", __name__, url_prefix="/audit")

    @blueprint.get("")
    @require_auth(session_service=session_service, allowed_roles=(Role.ADMINISTRATOR,))
    def list_audit():
        try:
            limit = int(request.args.get("limit", "50"))
        except ValueError:
            return jsonify({"message": "limit phải là số nguyên từ 1 đến 100."}), 400
        if not 1 <= limit <= 100:
            return jsonify({"message": "limit phải là số nguyên từ 1 đến 100."}), 400

        try:
            with session_factory() as session:
                ticket_rows = session.scalars(
                    select(TicketHistoryModel).order_by(
                        TicketHistoryModel.created_at.desc(), TicketHistoryModel.id.desc()
                    ).limit(limit)
                ).all()
                alert_rows = session.scalars(
                    select(AlertHistoryModel).order_by(
                        AlertHistoryModel.created_at.desc(), AlertHistoryModel.id.desc()
                    ).limit(limit)
                ).all()
                events = []
                for category, rows in (("ticket", ticket_rows), ("alert", alert_rows)):
                    for row in rows:
                        events.append({
                            "id": str(row.id),
                            "category": category,
                            "object_id": str(row.ticket_id if category == "ticket" else row.alert_id),
                            "actor_id": str(row.actor_id),
                            "action": row.action,
                            "from_status": row.from_status,
                            "to_status": row.to_status,
                            "created_at": row.created_at.isoformat(),
                        })
                events.sort(key=lambda event: (event["created_at"], event["id"]), reverse=True)
                return jsonify({"items": events[:limit]}), 200
        except SQLAlchemyError:
            return jsonify({"message": "Không thể tra cứu lịch sử lúc này."}), 503

    return blueprint
