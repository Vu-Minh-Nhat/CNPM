from abc import ABC, abstractmethod

from src.domain.models.asset import Node, Rack


class RackRepository(ABC):
    @abstractmethod
    def list_racks(self) -> list[Rack]:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, rack_id: str) -> Rack | None:
        raise NotImplementedError

    @abstractmethod
    def list_nodes(self, rack_id: str) -> list[Node]:
        raise NotImplementedError

    @abstractmethod
    def add(self, rack: Rack) -> Rack:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        rack_id: str,
        changes: dict[str, str | int],
    ) -> Rack | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, rack_id: str) -> bool:
        raise NotImplementedError