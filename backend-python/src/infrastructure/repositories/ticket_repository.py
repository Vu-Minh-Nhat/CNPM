from collections.abc import Callable
from typing import NoReturn
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DataError, DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from src.domain.exceptions import (
    ResourceConflictError,
    ValidationError,
)
from src.domain.models.ticket import Ticket
from src.domain.repositories.ticket_repository import TicketRepository
from src.infrastructure.models import TicketModel


class SqlAlchemyTicketRepository(TicketRepository):
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    @staticmethod
    def _to_domain(model: TicketModel) -> Ticket:
        return Ticket(
            id=str(model.id),
            node_id=str(model.node_id),
            alert_id=str(model.alert_id) if model.alert_id else None,
            created_by=str(model.created_by),
            assigned_to=str(model.assigned_to) if model.assigned_to else None,
            status=model.status,
            title=model.title,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _handle_write_error(error: DBAPIError) -> NoReturn:
        code = getattr(error.orig, "sqlstate", None)

        if code == "23503":
            raise ValidationError(
                "Node, alert hoặc tài khoản không tồn tại."
            ) from error

        if code in {"23502", "23514", "22001", "22P02"}:
            raise ValidationError(
                "Dữ liệu ticket không hợp lệ."
            ) from error

        if code == "23505":
            raise ResourceConflictError(
                "Ticket đã tồn tại."
            ) from error

        raise error

    @staticmethod
    def _normalize_uuid(value: str) -> str | None:
        try:
            return str(UUID(value))
        except (ValueError, TypeError, AttributeError):
            return None

    def save(self, ticket: Ticket) -> Ticket:
        try:
            with self._session_factory() as session:
                model = TicketModel(
                    id=ticket.id,
                    node_id=ticket.node_id,
                    alert_id=ticket.alert_id,
                    created_by=ticket.created_by,
                    assigned_to=ticket.assigned_to,
                    status=ticket.status,
                    title=ticket.title,
                    description=ticket.description,
                    created_at=ticket.created_at,
                    updated_at=ticket.updated_at,
                )

                session.add(model)
                session.commit()

                return self._to_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)

    def find_by_id(self, ticket_id: str) -> Ticket | None:
        normalized_id = self._normalize_uuid(ticket_id)

        if normalized_id is None:
            return None

        with self._session_factory() as session:
            model = session.get(TicketModel, normalized_id)

            if model is None:
                return None

            return self._to_domain(model)

    def list_by_node(
        self,
        node_id: str,
        status: str | None = None,
    ) -> list[Ticket]:
        normalized_id = self._normalize_uuid(node_id)

        if normalized_id is None:
            return []

        with self._session_factory() as session:
            statement = select(TicketModel).where(
                TicketModel.node_id == normalized_id
            )

            if status is not None:
                statement = statement.where(
                    TicketModel.status == status
                )

            statement = statement.order_by(
                TicketModel.created_at.desc(),
                TicketModel.id,
            )

            models = session.execute(statement).scalars().all()

            return [
                self._to_domain(model)
                for model in models
            ]

    def list_by_assignee(
        self,
        assigned_to: str,
        status: str | None = None,
    ) -> list[Ticket]:
        normalized_id = self._normalize_uuid(assigned_to)

        if normalized_id is None:
            return []

        with self._session_factory() as session:
            statement = select(TicketModel).where(
                TicketModel.assigned_to == normalized_id
            )

            if status is not None:
                statement = statement.where(
                    TicketModel.status == status
                )

            statement = statement.order_by(
                TicketModel.created_at.desc(),
                TicketModel.id,
            )

            models = session.execute(statement).scalars().all()

            return [
                self._to_domain(model)
                for model in models
            ]

    def list_by_alert(self, alert_id: str) -> list[Ticket]:
        normalized_id = self._normalize_uuid(alert_id)

        if normalized_id is None:
            return []

        with self._session_factory() as session:
            statement = (
                select(TicketModel)
                .where(TicketModel.alert_id == normalized_id)
                .order_by(
                    TicketModel.created_at.desc(),
                    TicketModel.id,
                )
            )

            models = session.execute(statement).scalars().all()

            return [
                self._to_domain(model)
                for model in models
            ]