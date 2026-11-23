
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
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.databases.base import Base


class AgentModel(Base):
    __tablename__ = "agents"

    __table_args__ = (
        CheckConstraint(
            "btrim(name) <> ''",
            name="ck_agents_name_not_blank",
        ),
        CheckConstraint(
            "length(certificate_fingerprint) = 64",
            name="ck_agents_fingerprint_length",
        ),
        UniqueConstraint(
            "certificate_fingerprint",
            name="uq_agents_certificate_fingerprint",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    certificate_fingerprint: Mapped[str] = mapped_column(
        String(64),
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


class AgentNodeAccessModel(Base):
    __tablename__ = "agent_node_access"

    __table_args__ = (
        Index(
            "ix_agent_node_access_node_id",
            "node_id",
        ),
    )

    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        primary_key=True,
    )

    node_id: Mapped[str] = mapped_column(
        ForeignKey("nodes.id", ondelete="RESTRICT"),
        primary_key=True,
    )
