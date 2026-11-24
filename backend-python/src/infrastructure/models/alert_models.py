
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.databases.base import Base


class AlertRuleModel(Base):
    __tablename__ = "alert_rules"

    __table_args__ = (
        CheckConstraint(
            """
            metric IN (
                'cpu_percent',
                'memory_percent',
                'disk_percent',
                'node_offline_seconds'
            )
            """,
            name="ck_alert_rules_metric",
        ),
        CheckConstraint(
            "operator IN ('>', '>=', '<', '<=')",
            name="ck_alert_rules_operator",
        ),
        CheckConstraint(
            """
            (
                metric IN ('cpu_percent', 'memory_percent', 'disk_percent')
                AND threshold >= 0
                AND threshold <= 100
            )
            OR
            (
                metric = 'node_offline_seconds'
                AND threshold >= 0
            )
            """,
            name="ck_alert_rules_threshold",
        ),
        CheckConstraint(
            """
            recovery_operator IS NULL
            OR recovery_operator IN ('>', '>=', '<', '<=')
            """,
            name="ck_alert_rules_recovery_operator",
        ),
        CheckConstraint(
            """
            recovery_threshold IS NULL
            OR
            (
                (
                    metric IN ('cpu_percent', 'memory_percent', 'disk_percent')
                    AND recovery_threshold >= 0
                    AND recovery_threshold <= 100
                )
                OR
                (
                    metric = 'node_offline_seconds'
                    AND recovery_threshold >= 0
                )
            )
            """,
            name="ck_alert_rules_recovery_threshold",
        ),
        CheckConstraint(
            "severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="ck_alert_rules_severity",
        ),
        Index(
            "ix_alert_rules_active_metric",
            "is_active",
            "metric",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    metric: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    operator: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    threshold: Mapped[float] = mapped_column(
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    recovery_operator: Mapped[str | None] = mapped_column(
        String(2),
        nullable=True,
    )

    recovery_threshold: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
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


class AlertModel(Base):
    __tablename__ = "alerts"

    __table_args__ = (
        CheckConstraint(
            """
            metric IN (
                'cpu_percent',
                'memory_percent',
                'disk_percent',
                'node_offline_seconds'
            )
            """,
            name="ck_alerts_metric",
        ),
        CheckConstraint(
            "operator IN ('>', '>=', '<', '<=')",
            name="ck_alerts_operator",
        ),
        CheckConstraint(
            """
            threshold IS NULL
            OR
            (
                (
                    metric IN ('cpu_percent', 'memory_percent', 'disk_percent')
                    AND threshold >= 0
                    AND threshold <= 100
                )
                OR
                (
                    metric = 'node_offline_seconds'
                    AND threshold >= 0
                )
            )
            """,
            name="ck_alerts_threshold",
        ),
        CheckConstraint(
            "severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="ck_alerts_severity",
        ),
        CheckConstraint(
            "status IN ('FIRING', 'ACKNOWLEDGED', 'RECOVERED')",
            name="ck_alerts_status",
        ),
        Index(
            "ix_alerts_node_status_time",
            "node_id",
            "status",
            "triggered_at",
        ),
        Index(
            "ix_alerts_rule_status",
            "rule_id",
            "status",
        ),
        Index(
            "uq_alerts_active_node_rule",
            "node_id",
            "rule_id",
            unique=True,
            postgresql_where=text(
                "rule_id IS NOT NULL "
                "AND status IN ('FIRING', 'ACKNOWLEDGED')"
            ),
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

    rule_id: Mapped[str | None] = mapped_column(
        ForeignKey("alert_rules.id", ondelete="RESTRICT"),
        nullable=True,
    )

    metric: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    operator: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    threshold: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    triggered_value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    severity: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    acknowledged_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )

    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    recovered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class AlertHistoryModel(Base):
    __tablename__ = "alert_history"

    __table_args__ = (
        Index(
            "ix_alert_history_alert_time",
            "alert_id",
            "created_at",
        ),
        Index(
            "ix_alert_history_actor_time",
            "actor_id",
            "created_at",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    alert_id: Mapped[str] = mapped_column(
        ForeignKey("alerts.id", ondelete="CASCADE"),
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
        String(16),
        nullable=True,
    )

    to_status: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )

    note: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
