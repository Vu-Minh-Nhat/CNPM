from flask import Blueprint, jsonify

from src.api.middleware import require_auth
from src.api.responses import asset_response
from src.domain.constants import Role
from src.services.assets_service import AssetsService
from src.services.session_service import SessionService


def create_assets_blueprint(
    assets_service: AssetsService,
    session_service: SessionService,
) -> Blueprint:
    blueprint = Blueprint("assets", __name__, url_prefix="/assets")

    @blueprint.get("")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def list_assets():
        nodes = assets_service.list_nodes()

        return jsonify([
            asset_response(node)
            for node in nodes
        ]), 200

    return blueprint