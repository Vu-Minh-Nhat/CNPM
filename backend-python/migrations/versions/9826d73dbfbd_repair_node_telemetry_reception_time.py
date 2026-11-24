"""repair node telemetry reception time

Revision ID: 9826d73dbfbd
Revises: 2e4fb41d32fd
Create Date: 2026-11-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9826d73dbfbd"
down_revision: Union[str, Sequence[str], None] = "2e4fb41d32fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the missing Node telemetry reception timestamp column."""

    op.add_column(
        "nodes",
        sa.Column(
            "last_telemetry_received_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove the Node telemetry reception timestamp column."""

    op.drop_column(
        "nodes",
        "last_telemetry_received_at",
    )
