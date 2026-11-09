from abc import ABC, abstractmethod

from src.domain.models.account import Account


class TokenProvider(ABC):
    @abstractmethod
    def issue(self, account: Account) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify(self, token: str) -> str:
        """Xác minh token và trả ID tài khoản."""
        raise NotImplementedError