
from flask import Blueprint, jsonify, request

from src.api.middleware import require_auth
from src.domain.constants import Role
from src.services.agent_service import AgentService
from src.services.session_service import SessionService


def create_agents_blueprint(
    agent_service: AgentService,
    session_service: SessionService,
) -> Blueprint:
    blueprint = Blueprint(
        "agents",
        __name__,
        url_prefix="/agents",
    )

    @blueprint.post("")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def register_agent():
        payload = request.get_json(silent=True)

        if not isinstance(payload, dict):
            return jsonify({
                "error": "Bad Request",
                "message": "Request body must be a JSON object",
                "statusCode": 400,
            }), 400

        try:
            agent = agent_service.register_agent(
                name=payload.get("name", ""),
                certificate_fingerprint=payload.get(
                    "certificate_fingerprint",
                    "",
                ),
            )
        except ValueError as exc:
            message = str(exc)

            if message == "Agent certificate already registered":
                return jsonify({
                    "error": "Conflict",
                    "message": message,
                    "statusCode": 409,
                }), 409

            return jsonify({
                "error": "Bad Request",
                "message": message,
                "statusCode": 400,
            }), 400

        return jsonify(agent), 201

    @blueprint.get("")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def list_agents():
        return jsonify(agent_service.list_agents()), 200

    @blueprint.get("/<agent_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def get_agent(agent_id):
        agent = agent_service.get_agent(agent_id)

        if agent is None:
            return jsonify({
                "error": "Not Found",
                "message": "Agent not found",
                "statusCode": 404,
            }), 404

        return jsonify(agent), 200

    @blueprint.patch("/<agent_id>/activate")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def activate_agent(agent_id):
        try:
            agent = agent_service.activate_agent(agent_id)
        except ValueError as exc:
            return jsonify({
                "error": "Not Found",
                "message": str(exc),
                "statusCode": 404,
            }), 404

        return jsonify(agent), 200

    @blueprint.patch("/<agent_id>/deactivate")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def deactivate_agent(agent_id):
        try:
            agent = agent_service.deactivate_agent(agent_id)
        except ValueError as exc:
            return jsonify({
                "error": "Not Found",
                "message": str(exc),
                "statusCode": 404,
            }), 404

        return jsonify(agent), 200

    @blueprint.post("/<agent_id>/nodes")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def assign_node(agent_id):
        payload = request.get_json(silent=True)

        if not isinstance(payload, dict):
            return jsonify({
                "error": "Bad Request",
                "message": "Request body must be a JSON object",
                "statusCode": 400,
            }), 400

        try:
            access = agent_service.assign_node(
                agent_id=agent_id,
                node_id=payload.get("node_id", ""),
            )
        except ValueError as exc:
            message = str(exc)

            if message == "Agent not found" or message == "Node not found":
                return jsonify({
                    "error": "Not Found",
                    "message": message,
                    "statusCode": 404,
                }), 404

            return jsonify({
                "error": "Bad Request",
                "message": message,
                "statusCode": 400,
            }), 400

        return jsonify(access), 201

    @blueprint.delete("/<agent_id>/nodes/<node_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def revoke_node(agent_id, node_id):
        try:
            revoked = agent_service.revoke_node(
                agent_id=agent_id,
                node_id=node_id,
            )
        except ValueError as exc:
            return jsonify({
                "error": "Not Found",
                "message": str(exc),
                "statusCode": 404,
            }), 404

        if not revoked:
            return jsonify({
                "error": "Not Found",
                "message": "Agent-Node access not found",
                "statusCode": 404,
            }), 404

        return jsonify({
            "message": "Node access revoked successfully",
            "agent_id": agent_id,
            "node_id": node_id,
        }), 200

    @blueprint.get("/<agent_id>/nodes")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def list_agent_nodes(agent_id):
        try:
            node_ids = agent_service.list_agent_nodes(agent_id)
        except ValueError as exc:
            return jsonify({
                "error": "Not Found",
                "message": str(exc),
                "statusCode": 404,
            }), 404

        return jsonify({
            "agent_id": agent_id,
            "node_ids": node_ids,
        }), 200

    return blueprint
