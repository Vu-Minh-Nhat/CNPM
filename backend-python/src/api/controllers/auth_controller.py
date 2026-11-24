from flask import Blueprint, g, jsonify, request

from src.api.middleware import require_auth
from src.domain.constants import Role
from src.domain.exceptions import AuthenticationError
from src.services.login_service import LoginService
from src.services.session_service import SessionService


def create_auth_blueprint(
    login_service: LoginService,
    session_service: SessionService,
) -> Blueprint:
    blueprint = Blueprint("auth", __name__, url_prefix="/auth")

    @blueprint.post("/login")
    def login():
        body = request.get_json(silent=True)

        if not isinstance(body, dict):
            return jsonify({
                "message": "Request phải chứa JSON object.",
                "error": "Bad Request",
                "statusCode": 400,
            }), 400

        email = body.get("email")
        password = body.get("password")

        if (
            not isinstance(email, str)
            or not email.strip()
            or not isinstance(password, str)
            or not password
        ):
            return jsonify({
                "message": "Email và mật khẩu là bắt buộc.",
                "error": "Bad Request",
                "statusCode": 400,
            }), 400

        try:
            result = login_service.login(email, password)
        except AuthenticationError as error:
            return jsonify({
                "message": str(error),
                "error": "Unauthorized",
                "statusCode": 401,
            }), 401

        return jsonify(result), 200

    @blueprint.get("/me")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def me():
        account = g.current_account

        return jsonify({
            "userId": account.id,
            "email": account.email,
            "role": account.role.value,
        }), 200

    return blueprint