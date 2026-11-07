from abc import ABC, abstractmethod

from src.domain.constants import Role
from src.domain.models.account import Account


class AccountRepository(ABC):
    @abstractmethod
    def find_by_email(self, email: str) -> Account | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, account_id: str) -> Account | None:
        raise NotImplementedError

    @abstractmethod
    def list_accounts(self) -> list[Account]:
        raise NotImplementedError

    @abstractmethod
    def add(self, account: Account) -> Account:
        raise NotImplementedError

    @abstractmethod
    def change_role(
        self,
        account_id: str,
        role: Role,
    ) -> Account | None:
        raise NotImplementedError