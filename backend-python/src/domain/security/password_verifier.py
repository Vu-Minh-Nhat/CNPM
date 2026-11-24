from abc import ABC, abstractmethod


class PasswordVerifier(ABC):
    @abstractmethod
    def verify(self, password: str, password_hash: str) -> bool:
        raise NotImplementedError