from collections.abc import Callable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.constants import Role
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