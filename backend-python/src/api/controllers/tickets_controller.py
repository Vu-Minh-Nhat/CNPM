from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from src.api.middleware import require_auth
from src.domain.constants import Role
from src.services.session_service import SessionService
from src.services.ticket_service import TicketService


def create_tickets_blueprint(
    ticket_service: TicketService,
    session_service: SessionService,
) -> Blueprint:
    blueprint = Blueprint(
        "tickets",
        __name__,
        url_prefix="/tickets",
    )

    @blueprint.errorhandler(SQLAlchemyError)
    def database_error(error):
        return jsonify({
            "message": "Không thể truy cập ticket lúc này.",
            "error": "Service Unavailable",
            "statusCode": 503,
        }), 503

    @blueprint.get("")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.OPERATOR, Role.TECHNICIAN),
    )
    def list_tickets():
        return jsonify(ticket_service.list_tickets(
            role=g.current_account.role,
            actor_id=str(g.current_account.id),
            status=request.args.get("status"),
        )), 200

    @blueprint.post("")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.OPERATOR,),
    )
    def create_ticket():
        result = ticket_service.create_ticket(
            actor_id=str(g.current_account.id),
            data=request.get_json(silent=True),
        )
        return jsonify(result), 201

    @blueprint.get("/<ticket_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.OPERATOR, Role.TECHNICIAN),
    )
    def get_ticket(ticket_id):
        return jsonify(ticket_service.get_ticket(
            ticket_id,
            role=g.current_account.role,
            actor_id=str(g.current_account.id),
        )), 200

    @blueprint.get("/<ticket_id>/history")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.OPERATOR, Role.TECHNICIAN),
    )
    def ticket_history(ticket_id):
        result = ticket_service.get_ticket(
            ticket_id,
            role=g.current_account.role,
            actor_id=str(g.current_account.id),
        )
        return jsonify(result["history"]), 200

    @blueprint.post("/<ticket_id>/assign")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.OPERATOR,),
    )
    def assign_ticket(ticket_id):
        result = ticket_service.assign_ticket(
            ticket_id,
            actor_id=str(g.current_account.id),
            data=request.get_json(silent=True),
        )
        return jsonify(result), 200

    @blueprint.post("/<ticket_id>/start")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.TECHNICIAN,),
    )
    def start_ticket(ticket_id):
        result = ticket_service.start_ticket(
            ticket_id,
            actor_id=str(g.current_account.id),
            data=request.get_json(silent=True),
        )
        return jsonify(result), 200

    @blueprint.patch("/<ticket_id>/work")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.TECHNICIAN,),
    )
    def update_work(ticket_id):
        result = ticket_service.update_work(
            ticket_id,
            actor_id=str(g.current_account.id),
            data=request.get_json(silent=True),
        )
        return jsonify(result), 200

    @blueprint.post("/<ticket_id>/submit")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.TECHNICIAN,),
    )
    def submit_for_approval(ticket_id):
        result = ticket_service.submit_for_approval(
            ticket_id,
            actor_id=str(g.current_account.id),
            data=request.get_json(silent=True),
        )
        return jsonify(result), 200

    @blueprint.post("/<ticket_id>/approve-close")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.OPERATOR,),
    )
    def approve_close(ticket_id):
        result = ticket_service.approve_close(
            ticket_id,
            actor_id=str(g.current_account.id),
            data=request.get_json(silent=True),
        )
        return jsonify(result), 200

    @blueprint.post("/<ticket_id>/return")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.OPERATOR,),
    )
    def return_for_work(ticket_id):
        result = ticket_service.return_for_work(
            ticket_id,
            actor_id=str(g.current_account.id),
            data=request.get_json(silent=True),
        )
        return jsonify(result), 200

    return blueprint
