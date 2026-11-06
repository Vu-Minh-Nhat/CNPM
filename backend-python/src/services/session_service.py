from src.domain.exceptions import AuthenticationError
from src.domain.models.account import Account
from src.domain.repositories.account_repository import AccountRepository
from src.domain.security.token_provider import TokenProvider


class SessionService:
    def __init__(
        self,
        accounts: AccountRepository,
        tokens: TokenProvider,
    ):
        self._accounts = accounts
        self._tokens = tokens

    def authenticate_token(self, token: str) -> Account:
        account_id = self._tokens.verify(token)
        account = self._accounts.find_by_id(account_id)

        if account is None or not account.is_active:
            raise AuthenticationError(
                "Tài khoản không tồn tại hoặc đã bị khóa."
            )

        return account