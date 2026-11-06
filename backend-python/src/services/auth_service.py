from src.domain.exceptions import AuthenticationError
from src.domain.models.account import Account
from src.domain.repositories.account_repository import AccountRepository
from src.domain.security.password_verifier import PasswordVerifier


class AuthService:
    def __init__(
        self,
        account_repository: AccountRepository,
        password_verifier: PasswordVerifier,
    ):
        self._accounts = account_repository
        self._password_verifier = password_verifier

    def authenticate(self, email: str, password: str) -> Account:
        if (
            not isinstance(email, str)
            or not email.strip()
            or not isinstance(password, str)
            or not password
        ):
            raise AuthenticationError("Sai email hoặc mật khẩu.")

        account = self._accounts.find_by_email(email)

        if account is None or not account.is_active:
            raise AuthenticationError("Sai email hoặc mật khẩu.")

        if not self._password_verifier.verify(
            password,
            account.password_hash,
        ):
            raise AuthenticationError("Sai email hoặc mật khẩu.")

        return account