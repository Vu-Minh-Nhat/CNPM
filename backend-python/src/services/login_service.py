from src.domain.security.token_provider import TokenProvider
from src.services.auth_service import AuthService


class LoginService:
    def __init__(
        self,
        auth_service: AuthService,
        token_provider: TokenProvider,
    ):
        self._auth_service = auth_service
        self._token_provider = token_provider

    def login(self, email: str, password: str) -> dict[str, str]:
        account = self._auth_service.authenticate(email, password)

        return {
            "accessToken": self._token_provider.issue(account),
            "role": account.role.value,
        }