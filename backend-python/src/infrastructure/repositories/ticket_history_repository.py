from collections.abc import Callable
from typing import NoReturn
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DataError, DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from src.domain.exceptions import ValidationError
from src.domain.models.ticket_history import TicketHistory
from src.domain.repositories.ticket_history_repository import (
    TicketHistoryRepository,
)
from src.infrastructure.models import TicketHistoryModel


class SqlAlchemyTicketHistoryRepository(TicketHistoryRepository):
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    @staticmethod
    def _to_domain(model: TicketHistoryModel) -> TicketHistory:
        return TicketHistory(
            id=str(model.id),
            ticket_id=str(model.ticket_id),
            actor_id=str(model.actor_id),
            action=model.action,
            from_status=model.from_status,
            to_status=model.to_status,
            note=model.note,
            created_at=model.created_at,
        )

    @staticmethod
    def _handle_write_error(error: DBAPIError) -> NoReturn:
        code = getattr(error.orig, "sqlstate", None)

        if code == "23503":
            raise ValidationError(
                "Ticket hoặc tài khoản thực hiện không tồn tại."
            ) from error

        if code in {"23502", "23514", "22001", "22P02"}:
            raise ValidationError(
                "Dữ liệu lịch sử ticket không hợp lệ."
            ) from error

        raise error

    @staticmethod
    def _normalize_uuid(value: str) -> str | None:
        try:
            return str(UUID(value))
        except (ValueError, TypeError, AttributeError):
            return None

    def save(self, history: TicketHistory) -> TicketHistory:
        try:
            with self._session_factory() as session:
                model = TicketHistoryModel(
                    id=history.id,
                    ticket_id=history.ticket_id,
                    actor_id=history.actor_id,
                    action=history.action,
                    from_status=history.from_status,
                    to_status=history.to_status,
                    note=history.note,
                    created_at=history.created_at,
                )

                session.add(model)
                session.commit()

                return self._to_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)

    def list_by_ticket(self, ticket_id: str) -> list[TicketHistory]:
        normalized_id = self._normalize_uuid(ticket_id)

        if normalized_id is None:
            return []

        with self._session_factory() as session:
            statement = (
                select(TicketHistoryModel)
                .where(TicketHistoryModel.ticket_id == normalized_id)
                .order_by(
                    TicketHistoryModel.created_at.asc(),
                    TicketHistoryModel.id,
                )
            )

            models = session.execute(statement).scalars().all()

            return [
                self._to_domain(model)
                for model in models
            ]

    def list_by_actor(self, actor_id: str) -> list[TicketHistory]:
        normalized_id = self._normalize_uuid(actor_id)

        if normalized_id is None:
            return []

        with self._session_factory() as session:
            statement = (
                select(TicketHistoryModel)
                .where(TicketHistoryModel.actor_id == normalized_id)
                .order_by(
                    TicketHistoryModel.created_at.desc(),
                    TicketHistoryModel.id,
                )
            )

            models = session.execute(statement).scalars().all()

            return [
                self._to_domain(model)
                for model in models
            ]