from abc import ABC, abstractmethod

from src.domain.models.asset import Node


class AssetRepository(ABC):
    @abstractmethod
    def list_nodes(self) -> list[Node]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, node_id: str) -> Node | None:
        raise NotImplementedError