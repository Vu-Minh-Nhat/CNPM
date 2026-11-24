from abc import ABC, abstractmethod

from src.domain.models.ticket import Ticket
from src.domain.models.ticket_history import TicketHistory


class TicketRepository(ABC):
    @abstractmethod
    def create_with_history(
        self,
        ticket: Ticket,
        history: TicketHistory,
    ) -> Ticket:
        raise NotImplementedError

    @abstractmethod
    def update_with_history(
        self,
        ticket_id: str,
        expected_version: int,
        changes: dict,
        history: TicketHistory,
    ) -> Ticket | None:
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

    @abstractmethod
    def list_all(self, status: str | None = None) -> list[Ticket]:
        raise NotImplementedError
