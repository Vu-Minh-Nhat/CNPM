from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.databases.base import Base


class MarkerModel(Base):
    __tablename__ = "markers"

    __table_args__ = (
        UniqueConstraint(
            "marker_type",
            "identifier",
            name="uq_markers_type_identifier",
        ),
        CheckConstraint(
            "btrim(marker_type) <> ''",
            name="ck_markers_type_not_blank",
        ),
        CheckConstraint(
            "btrim(identifier) <> ''",
            name="ck_markers_identifier_not_blank",
        ),
        Index(
            "ix_markers_node_id",
            "node_id",
        ),
        Index(
            "ix_markers_active_lookup",
            "marker_type",
            "identifier",
            "is_active",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
    )

    marker_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    identifier: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    node_id: Mapped[str] = mapped_column(
        ForeignKey("nodes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("true"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    node = relationship("NodeModel")