from flask import Blueprint, jsonify, request

from src.api.middleware import require_auth
from src.api.responses import asset_response
from src.domain.constants import Role
from src.services.servers_service import ServersService
from src.services.session_service import SessionService


def create_servers_blueprint(
    servers_service: ServersService,
    session_service: SessionService,
) -> Blueprint:
    blueprint = Blueprint("servers", __name__, url_prefix="/servers")

    @blueprint.get("")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def list_servers():
        servers = servers_service.list_servers()

        return jsonify([
            asset_response(server)
            for server in servers
        ]), 200

    @blueprint.get("/<server_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def get_server(server_id):
        server = servers_service.get_server(server_id)
        return jsonify(asset_response(server)), 200

    @blueprint.post("")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR, Role.OPERATOR),
    )
    def create_server():
        server = servers_service.create(
            request.get_json(silent=True)
        )

        return jsonify(asset_response(server)), 201

    @blueprint.patch("/<server_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR, Role.OPERATOR),
    )
    def update_server(server_id):
        server = servers_service.update(
            server_id,
            request.get_json(silent=True),
        )

        return jsonify(asset_response(server)), 200

    @blueprint.delete("/<server_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def delete_server(server_id):
        servers_service.delete(server_id)

        return jsonify({
            "message": "Xóa Server thành công",
        }), 200

    return blueprint