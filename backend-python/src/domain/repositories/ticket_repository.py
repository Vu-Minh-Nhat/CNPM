from abc import ABC, abstractmethod

from src.domain.models.ticket import Ticket


class TicketRepository(ABC):
    @abstractmethod
    def save(self, ticket: Ticket) -> Ticket:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, ticket_id: str) -> Ticket | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_node(
        self,
        node_id: str,
        status: str | None = None,
    ) -> list[Ticket]:
        raise NotImplementedError

    @abstractmethod
    def list_by_assignee(
        self,
        assigned_to: str,
        status: str | None = None,
    ) -> list[Ticket]:
        raise NotImplementedError

    @abstractmethod
    def list_by_alert(self, alert_id: str) -> list[Ticket]:
        raise NotImplementedError