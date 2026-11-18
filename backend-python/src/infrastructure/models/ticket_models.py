import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.databases.base import Base


class TicketModel(Base):
    __tablename__ = "tickets"

    __table_args__ = (
        CheckConstraint(
            "status IN ('NEW', 'ASSIGNED', 'IN_PROGRESS', "
            "'PENDING_APPROVAL', 'CLOSED')",
            name="ck_tickets_status",
        ),
        Index(
            "ix_tickets_node_status_time",
            "node_id",
            "status",
            "created_at",
        ),
        Index(
            "ix_tickets_assigned_status",
            "assigned_to",
            "status",
        ),
        Index(
            "ix_tickets_created_at",
            "created_at",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    node_id: Mapped[str] = mapped_column(
        ForeignKey("nodes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    alert_id: Mapped[str | None] = mapped_column(
        ForeignKey("alerts.id", ondelete="RESTRICT"),
        nullable=True,
    )

    created_by: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    assigned_to: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default="NEW",
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(4000),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class TicketHistoryModel(Base):
    __tablename__ = "ticket_history"

    __table_args__ = (
        Index(
            "ix_ticket_history_ticket_time",
            "ticket_id",
            "created_at",
        ),
        Index(
            "ix_ticket_history_actor_time",
            "actor_id",
            "created_at",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    ticket_id: Mapped[str] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
    )

    actor_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    from_status: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    to_status: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    note: Mapped[str | None] = mapped_column(
        String(4000),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )