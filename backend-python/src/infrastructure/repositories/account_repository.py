from collections.abc import Callable
from typing import NoReturn
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DataError, DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from src.domain.constants import Role
from src.domain.exceptions import (
    ResourceConflictError,
    ValidationError,
)
from src.domain.models.account import Account
from src.domain.repositories.account_repository import AccountRepository
from src.infrastructure.models import AccountModel


class SqlAlchemyAccountRepository(AccountRepository):
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    @staticmethod
    def _to_domain(model: AccountModel) -> Account:
        return Account(
            id=str(model.id),
            email=model.email,
            role=Role(model.role_code),
            is_active=model.is_active,
            password_hash=model.password_hash,
        )

    @staticmethod
    def _handle_write_error(error: DBAPIError) -> NoReturn:
        code = getattr(error.orig, "sqlstate", None)

        if code == "23505":
            raise ResourceConflictError(
                "Email đã tồn tại."
            ) from error

        if code == "23503":
            raise ValidationError(
                "Vai trò không tồn tại."
            ) from error

        if code in {"23502", "23514", "22001"}:
            raise ValidationError(
                "Dữ liệu tài khoản không hợp lệ."
            ) from error

        raise error

    def find_by_email(self, email: str) -> Account | None:
        normalized_email = email.strip().lower()

        with self._session_factory() as session:
            statement = select(AccountModel).where(
                AccountModel.email == normalized_email
            )

            model = session.execute(statement).scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)

    def find_by_id(self, account_id: str) -> Account | None:
        try:
            normalized_id = str(UUID(account_id))
        except (ValueError, TypeError, AttributeError):
            return None

        with self._session_factory() as session:
            model = session.get(AccountModel, normalized_id)

            if model is None:
                return None

            return self._to_domain(model)

    def list_accounts(self) -> list[Account]:
        with self._session_factory() as session:
            statement = select(AccountModel).order_by(
                AccountModel.email
            )

            models = session.execute(statement).scalars().all()

            return [
                self._to_domain(model)
                for model in models
            ]

    def add(self, account: Account) -> Account:
        try:
            with self._session_factory() as session:
                model = AccountModel(
                    id=account.id,
                    email=account.email,
                    password_hash=account.password_hash,
                    role_code=account.role.value,
                    is_active=account.is_active,
                )

                session.add(model)
                session.commit()

                return self._to_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)

    def change_role(
        self,
        account_id: str,
        role: Role,
    ) -> Account | None:
        try:
            normalized_id = str(UUID(account_id))
        except (ValueError, TypeError, AttributeError):
            return None

        try:
            with self._session_factory() as session:
                model = session.get(AccountModel, normalized_id)

                if model is None:
                    return None

                model.role_code = role.value
                session.commit()

                return self._to_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)