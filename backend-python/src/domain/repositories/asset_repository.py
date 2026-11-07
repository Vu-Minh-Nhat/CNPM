from abc import ABC, abstractmethod

from src.domain.models.asset import Node


class AssetRepository(ABC):
    @abstractmethod
    def list_nodes(self) -> list[Node]:
        raise NotImplementedError