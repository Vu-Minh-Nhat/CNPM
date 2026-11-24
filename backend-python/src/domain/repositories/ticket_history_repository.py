from abc import ABC, abstractmethod

from src.domain.models.ticket_history import TicketHistory


class TicketHistoryRepository(ABC):
    @abstractmethod
    def save(self, history: TicketHistory) -> TicketHistory:
        raise NotImplementedError

    @abstractmethod
    def list_by_ticket(self, ticket_id: str) -> list[TicketHistory]:
        raise NotImplementedError

    @abstractmethod
    def list_by_actor(self, actor_id: str) -> list[TicketHistory]:
        raise NotImplementedError