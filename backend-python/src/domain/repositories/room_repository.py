from abc import ABC, abstractmethod

from src.domain.models.asset import Rack, Room


class RoomRepository(ABC):
    @abstractmethod
    def list_rooms(self) -> list[Room]:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, room_id: str) -> Room | None:
        raise NotImplementedError

    @abstractmethod
    def list_racks(self, room_id: str) -> list[Rack]:
        raise NotImplementedError

    @abstractmethod
    def add(self, room: Room) -> Room:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        room_id: str,
        changes: dict[str, str],
    ) -> Room | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, room_id: str) -> bool:
        raise NotImplementedError