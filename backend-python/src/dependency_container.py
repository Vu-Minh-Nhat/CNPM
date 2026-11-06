from dataclasses import dataclass

from src.domain.repositories.account_repository import AccountRepository
from src.domain.security.token_provider import TokenProvider
from src.infrastructure.databases.database import Database
from src.infrastructure.repositories.account_repository import (
    SqlAlchemyAccountRepository,
)
from src.infrastructure.security.bcrypt_password_verifier import (
    BcryptPasswordVerifier,
)
from src.infrastructure.security.jwt_token_provider import JwtTokenProvider
from src.services.auth_service import AuthService
from src.services.login_service import LoginService
from src.services.session_service import SessionService
from src.services.users_service import UsersService


@dataclass(frozen=True)
class Container:
    accounts: AccountRepository
    tokens: TokenProvider
    login_service: LoginService
    session_service: SessionService
    users_service: UsersService


def build_container(
    database: Database,
    jwt_secret: str,
    jwt_expires_in_seconds: int,
) -> Container:
    accounts = SqlAlchemyAccountRepository(
        session_factory=database.create_session,
    )

    tokens = JwtTokenProvider(
        secret=jwt_secret,
        expires_in_seconds=jwt_expires_in_seconds,
    )

    auth_service = AuthService(
        account_repository=accounts,
        password_verifier=BcryptPasswordVerifier(),
    )

    return Container(
        accounts=accounts,
        tokens=tokens,
        login_service=LoginService(
            auth_service=auth_service,
            token_provider=tokens,
        ),
        session_service=SessionService(
            accounts=accounts,
            tokens=tokens,
        ),
        users_service=UsersService(
            accounts=accounts,
        ),
    )