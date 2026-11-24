from getpass import getpass

from src.create_app import create_app
from src.domain.exceptions import AuthenticationError
from src.infrastructure.repositories.account_repository import (
    SqlAlchemyAccountRepository,
)
from src.infrastructure.security.bcrypt_password_verifier import (
    BcryptPasswordVerifier,
)
from src.services.auth_service import AuthService


def check_login() -> None:
    app = create_app()
    database = app.extensions["database"]

    service = AuthService(
        account_repository=SqlAlchemyAccountRepository(
            session_factory=database.create_session,
        ),
        password_verifier=BcryptPasswordVerifier(),
    )

    try:
        email = input("Email: ").strip()
        password = getpass("Mật khẩu: ")

        try:
            account = service.authenticate(email, password)
        except AuthenticationError as error:
            print(f"Đăng nhập thất bại: {error}")
            return

        print("Xác thực thành công.")
        print(f"Email: {account.email}")
        print(f"Role: {account.role.value}")
    finally:
        database.dispose()


if __name__ == "__main__":
    check_login()