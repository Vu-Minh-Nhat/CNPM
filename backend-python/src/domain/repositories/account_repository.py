from abc import ABC, abstractmethod

from src.domain.models.account import Account


class AccountRepository(ABC):
    @abstractmethod
    def find_by_email(self, email: str) -> Account | None:
        """Tìm tài khoản theo email."""
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, account_id: str) -> Account | None:
        """Tìm tài khoản theo ID."""
        raise NotImplementedError
    @abstractmethod
    def list_accounts(self) -> list[Account]:
        """Lấy danh sách tài khoản."""
        raise NotImplementedError