from flask import Blueprint, jsonify, request

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

    @blueprint.post("")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def create_account():
        account = users_service.create(
            request.get_json(silent=True)
        )

        return jsonify(account), 201

    @blueprint.patch("/<account_id>/role")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def change_role(account_id):
        account = users_service.change_role(
            account_id,
            request.get_json(silent=True),
        )

        return jsonify(account), 200

    return blueprint