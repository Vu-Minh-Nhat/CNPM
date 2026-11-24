
"""add alert acknowledgement history

Revision ID: d4a7f9c2e610
Revises: c91e4f2a7b30
Create Date: 2026-11-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "d4a7f9c2e610"
down_revision: Union[str, Sequence[str], None] = "c91e4f2a7b30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the actual value that triggered the alert.
    op.add_column(
        "alerts",
        sa.Column(
            "triggered_value",
            sa.Float(),
            nullable=True,
        ),
    )

    # Store the account that acknowledged the alert.
    op.add_column(
        "alerts",
        sa.Column(
            "acknowledged_by",
            postgresql.UUID(as_uuid=False),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_alerts_acknowledged_by_users",
        "alerts",
        "users",
        ["acknowledged_by"],
        ["id"],
        ondelete="RESTRICT",
    )

    # Store alert lifecycle and acknowledgement history.
    op.create_table(
        "alert_history",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "alert_id",
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
            sa.String(length=16),
            nullable=True,
        ),
        sa.Column(
            "to_status",
            sa.String(length=16),
            nullable=True,
        ),
        sa.Column(
            "note",
            sa.String(length=1000),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["alert_id"],
            ["alerts.id"],
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
        "ix_alert_history_alert_time",
        "alert_history",
        ["alert_id", "created_at"],
    )

    op.create_index(
        "ix_alert_history_actor_time",
        "alert_history",
        ["actor_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_alert_history_actor_time",
        table_name="alert_history",
    )

    op.drop_index(
        "ix_alert_history_alert_time",
        table_name="alert_history",
    )

    op.drop_table("alert_history")

    op.drop_constraint(
        "fk_alerts_acknowledged_by_users",
        "alerts",
        type_="foreignkey",
    )

    op.drop_column("alerts", "acknowledged_by")
    op.drop_column("alerts", "triggered_value")
