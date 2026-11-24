"""add alert ticket storage

Revision ID: 37ef391dbfde
Revises: 06a7c693c5bf
Create Date: 2026-11-18 16:15:54.393444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "37ef391dbfde"
down_revision: Union[str, Sequence[str], None] = "06a7c693c5bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create alert and ticket storage tables."""

    op.create_table(
        "alert_rules",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "metric",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "operator",
            sa.String(length=2),
            nullable=False,
        ),
        sa.Column(
            "threshold",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.String(length=16),
            nullable=False,
        ),
        sa.Column(
            "recovery_operator",
            sa.String(length=2),
            nullable=True,
        ),
        sa.Column(
            "recovery_threshold",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "metric IN ('cpu_percent', 'memory_percent', 'disk_percent')",
            name="ck_alert_rules_metric",
        ),
        sa.CheckConstraint(
            "operator IN ('>', '>=', '<', '<=')",
            name="ck_alert_rules_operator",
        ),
        sa.CheckConstraint(
            "threshold >= 0 AND threshold <= 100",
            name="ck_alert_rules_threshold",
        ),
        sa.CheckConstraint(
            "recovery_operator IS NULL OR "
            "recovery_operator IN ('>', '>=', '<', '<=')",
            name="ck_alert_rules_recovery_operator",
        ),
        sa.CheckConstraint(
            "recovery_threshold IS NULL OR "
            "(recovery_threshold >= 0 AND recovery_threshold <= 100)",
            name="ck_alert_rules_recovery_threshold",
        ),
        sa.CheckConstraint(
            "severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="ck_alert_rules_severity",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_alert_rules_active_metric",
        "alert_rules",
        ["is_active", "metric"],
    )

    op.create_table(
        "alerts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "node_id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "rule_id",
            postgresql.UUID(as_uuid=False),
            nullable=True,
        ),
        sa.Column(
            "metric",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "operator",
            sa.String(length=2),
            nullable=False,
        ),
        sa.Column(
            "threshold",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "severity",
            sa.String(length=16),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
        ),
        sa.Column(
            "message",
            sa.String(length=1000),
            nullable=False,
        ),
        sa.Column(
            "triggered_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "acknowledged_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "recovered_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "metric IN ('cpu_percent', 'memory_percent', 'disk_percent')",
            name="ck_alerts_metric",
        ),
        sa.CheckConstraint(
            "operator IN ('>', '>=', '<', '<=')",
            name="ck_alerts_operator",
        ),
        sa.CheckConstraint(
            "threshold IS NULL OR "
            "(threshold >= 0 AND threshold <= 100)",
            name="ck_alerts_threshold",
        ),
        sa.CheckConstraint(
            "severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="ck_alerts_severity",
        ),
        sa.CheckConstraint(
            "status IN ('FIRING', 'ACKNOWLEDGED', 'RECOVERED')",
            name="ck_alerts_status",
        ),
        sa.ForeignKeyConstraint(
            ["node_id"],
            ["nodes.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["rule_id"],
            ["alert_rules.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_alerts_node_status_time",
        "alerts",
        ["node_id", "status", "triggered_at"],
    )

    op.create_index(
        "ix_alerts_rule_status",
        "alerts",
        ["rule_id", "status"],
    )

    op.create_index(
        "uq_alerts_active_node_rule",
        "alerts",
        ["node_id", "rule_id"],
        unique=True,
        postgresql_where=sa.text(
            "rule_id IS NOT NULL "
            "AND status IN ('FIRING', 'ACKNOWLEDGED')"
        ),
    )

    op.create_table(
        "tickets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "node_id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "alert_id",
            postgresql.UUID(as_uuid=False),
            nullable=True,
        ),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "assigned_to",
            postgresql.UUID(as_uuid=False),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default=sa.text("'NEW'"),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.String(length=4000),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('NEW', 'ASSIGNED', 'IN_PROGRESS', "
            "'PENDING_APPROVAL', 'CLOSED')",
            name="ck_tickets_status",
        ),
        sa.ForeignKeyConstraint(
            ["node_id"],
            ["nodes.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["alert_id"],
            ["alerts.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["assigned_to"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_tickets_node_status_time",
        "tickets",
        ["node_id", "status", "created_at"],
    )

    op.create_index(
        "ix_tickets_assigned_status",
        "tickets",
        ["assigned_to", "status"],
    )

    op.create_index(
        "ix_tickets_created_at",
        "tickets",
        ["created_at"],
    )

    op.create_table(
        "ticket_history",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "ticket_id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "actor_id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "action",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "from_status",
            sa.String(length=32),
            nullable=True,
        ),
        sa.Column(
            "to_status",
            sa.String(length=32),
            nullable=True,
        ),
        sa.Column(
            "note",
            sa.String(length=4000),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["tickets.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_ticket_history_ticket_time",
        "ticket_history",
        ["ticket_id", "created_at"],
    )

    op.create_index(
        "ix_ticket_history_actor_time",
        "ticket_history",
        ["actor_id", "created_at"],
    )


def downgrade() -> None:
    """Drop alert and ticket storage tables."""

    op.drop_index(
        "ix_ticket_history_actor_time",
        table_name="ticket_history",
    )
    op.drop_index(
        "ix_ticket_history_ticket_time",
        table_name="ticket_history",
    )
    op.drop_table("ticket_history")

    op.drop_index(
        "ix_tickets_created_at",
        table_name="tickets",
    )
    op.drop_index(
        "ix_tickets_assigned_status",
        table_name="tickets",
    )
    op.drop_index(
        "ix_tickets_node_status_time",
        table_name="tickets",
    )
    op.drop_table("tickets")

    op.drop_index(
        "uq_alerts_active_node_rule",
        table_name="alerts",
    )
    op.drop_index(
        "ix_alerts_rule_status",
        table_name="alerts",
    )
    op.drop_index(
        "ix_alerts_node_status_time",
        table_name="alerts",
    )
    op.drop_table("alerts")

    op.drop_index(
        "ix_alert_rules_active_metric",
        table_name="alert_rules",
    )
    op.drop_table("alert_rules")