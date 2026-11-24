from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.databases.base import Base


class TelemetryModel(Base):
    __tablename__ = "node_telemetry"

    __table_args__ = (
        UniqueConstraint(
            "node_id",
            "message_id",
            name="uq_node_telemetry_node_message",
        ),
        CheckConstraint(
            "cpu_percent >= 0 AND cpu_percent <= 100",
            name="ck_node_telemetry_cpu_percent",
        ),
        CheckConstraint(
            "memory_percent >= 0 AND memory_percent <= 100",
            name="ck_node_telemetry_memory_percent",
        ),
        CheckConstraint(
            "disk_percent >= 0 AND disk_percent <= 100",
            name="ck_node_telemetry_disk_percent",
        ),
        Index(
            "ix_node_telemetry_node_time",
            "node_id",
            "measured_at",
            "received_at",
            "id",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    message_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
    )

    node_id: Mapped[str] = mapped_column(
        ForeignKey("nodes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    cpu_percent: Mapped[float] = mapped_column(
        Float(precision=53),
        nullable=False,
    )

    memory_percent: Mapped[float] = mapped_column(
        Float(precision=53),
        nullable=False,
    )

    disk_percent: Mapped[float] = mapped_column(
        Float(precision=53),
        nullable=False,
    )