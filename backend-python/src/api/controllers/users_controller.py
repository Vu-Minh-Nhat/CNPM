from flask import Blueprint, jsonify

from src.api.middleware import require_auth
from src.domain.constants import Role
from src.services.session_service import SessionService
from src.services.users_service import UsersService


def create_users_blueprint(
    users_service: UsersService,
    session_service: SessionService,
) -> Blueprint:
    blueprint = Blueprint("users", __name__, url_prefix="/users")

    @blueprint.get("")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def list_accounts():
        return jsonify(users_service.list_accounts()), 200

    return blueprint