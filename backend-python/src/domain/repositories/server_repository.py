from abc import ABC, abstractmethod

from src.domain.models.asset import Node


class ServerRepository(ABC):
    @abstractmethod
    def list_servers(self) -> list[Node]:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, server_id: str) -> Node | None:
        raise NotImplementedError

    @abstractmethod
    def add(self, server: Node) -> Node:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        server_id: str,
        changes: dict[str, str | None],
    ) -> Node | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, server_id: str) -> bool:
        raise NotImplementedError