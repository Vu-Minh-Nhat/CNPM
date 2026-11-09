import re
from uuid import UUID, uuid4

from src.domain.constants import Role
from src.domain.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)
from src.domain.models.account import Account
from src.domain.repositories.account_repository import AccountRepository
from src.domain.security.password_hasher import PasswordHasher


class UsersService:
    def __init__(
        self,
        accounts: AccountRepository,
        password_hasher: PasswordHasher,
    ):
        self._accounts = accounts
        self._password_hasher = password_hasher

    @staticmethod
    def _public_account(account: Account) -> dict:
        return {
            "id": account.id,
            "email": account.email,
            "role": account.role.value,
            "isActive": account.is_active,
        }

    @staticmethod
    def _validate_role(value: object) -> Role:
        if not isinstance(value, str):
            raise ValidationError("Vai trò không hợp lệ.")

        try:
            return Role(value)
        except ValueError as error:
            raise ValidationError(
                "Vai trò không hợp lệ."
            ) from error

    def list_accounts(self) -> list[dict]:
        return [
            self._public_account(account)
            for account in self._accounts.list_accounts()
        ]

    def create(self, data: object) -> dict:
        required_fields = {"email", "password", "role"}

        if not isinstance(data, dict):
            raise ValidationError("Dữ liệu phải là JSON object.")

        if set(data) != required_fields:
            raise ValidationError(
                "Chỉ chấp nhận và yêu cầu đủ email, password, role."
            )

        email = data["email"]
        password = data["password"]

        if not isinstance(email, str):
            raise ValidationError("Email không hợp lệ.")

        email = email.strip().lower()

        if (
            len(email) > 254
            or re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) is None
        ):
            raise ValidationError("Email không hợp lệ.")

        if (
            not isinstance(password, str)
            or len(password) < 8
            or len(password.encode("utf-8")) > 72
        ):
            raise ValidationError(
                "Mật khẩu phải từ 8 ký tự và tối đa 72 byte UTF-8."
            )

        role = self._validate_role(data["role"])

        if self._accounts.find_by_email(email) is not None:
            raise ResourceConflictError("Email đã tồn tại.")

        account = Account(
            id=str(uuid4()),
            email=email,
            role=role,
            is_active=True,
            password_hash=self._password_hasher.hash_password(password),
        )

        created = self._accounts.add(account)

        return self._public_account(created)

    def change_role(self, account_id: str, data: object) -> dict:
        try:
            normalized_id = str(UUID(account_id))
        except (ValueError, TypeError, AttributeError) as error:
            raise ValidationError(
                "ID tài khoản phải là UUID hợp lệ."
            ) from error

        if not isinstance(data, dict) or set(data) != {"role"}:
            raise ValidationError(
                "Cần cung cấp duy nhất trường role."
            )

        role = self._validate_role(data["role"])

        account = self._accounts.change_role(
            normalized_id,
            role,
        )

        if account is None:
            raise ResourceNotFoundError(
                "Không tìm thấy tài khoản."
            )

        return self._public_account(account)