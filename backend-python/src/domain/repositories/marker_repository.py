from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.models.marker import Marker


class MarkerRepository(ABC):
    @abstractmethod
    def create(self, marker: Marker) -> Marker:
        pass

    @abstractmethod
    def get_by_id(self, marker_id: str) -> Marker | None:
        pass

    @abstractmethod
    def get_by_identifier(
        self,
        marker_type: str,
        identifier: str,
    ) -> Marker | None:
        pass

    @abstractmethod
    def list_all(self) -> Sequence[Marker]:
        pass

    @abstractmethod
    def update(self, marker: Marker) -> Marker:
        pass