from functools import wraps

from flask import g, jsonify, request

from src.domain.constants import Role
from src.domain.exceptions import AuthenticationError
from src.services.session_service import SessionService


def require_auth(
    session_service: SessionService,
    allowed_roles: tuple[Role, ...],
):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            authorization = request.headers.get("Authorization", "")
            parts = authorization.split()

            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({
                    "message": "Thiếu hoặc sai Authorization header.",
                    "error": "Unauthorized",
                    "statusCode": 401,
                }), 401

            try:
                account = session_service.authenticate_token(parts[1])
            except AuthenticationError as error:
                return jsonify({
                    "message": str(error),
                    "error": "Unauthorized",
                    "statusCode": 401,
                }), 401

            if account.role not in allowed_roles:
                return jsonify({
                    "message": "Bạn không có quyền thực hiện thao tác này.",
                    "error": "Forbidden",
                    "statusCode": 403,
                }), 403

            g.current_account = account

            return view(*args, **kwargs)

        return wrapped

    return decorator