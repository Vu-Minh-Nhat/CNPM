import os

from src.create_app import create_app
from src.domain.exceptions import AuthenticationError
from src.infrastructure.repositories.account_repository import (
    SqlAlchemyAccountRepository,
)
from src.infrastructure.security.jwt_token_provider import JwtTokenProvider


def check_jwt() -> None:
    app = create_app()
    database = app.extensions["database"]

    try:
        repository = SqlAlchemyAccountRepository(
            session_factory=database.create_session,
        )

        account = repository.find_by_email("admin@arimms.local")

        if account is None:
            raise RuntimeError("Không tìm thấy tài khoản admin.")

        provider = JwtTokenProvider(
            secret=os.getenv("JWT_SECRET", ""),
            expires_in_seconds=int(
                os.getenv("JWT_EXPIRES_IN_SECONDS", "86400")
            ),
        )

        token = provider.issue(account)
        account_id = provider.verify(token)

        if account_id != account.id:
            raise RuntimeError("ID tài khoản trong token không khớp.")

        print("Tạo JWT: OK")
        print("Xác minh JWT và ID tài khoản: OK")

        try:
            provider.verify("invalid.token.value")
        except AuthenticationError:
            print("Token sai bị từ chối: OK")
        else:
            raise RuntimeError("Token sai chưa bị từ chối.")
    finally:
        database.dispose()


if __name__ == "__main__":
    check_jwt()