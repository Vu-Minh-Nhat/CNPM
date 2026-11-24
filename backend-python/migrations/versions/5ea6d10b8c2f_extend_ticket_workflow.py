"""extend ticket workflow

Revision ID: 5ea6d10b8c2f
Revises: d4a7f9c2e610
Create Date: 2026-11-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "5ea6d10b8c2f"
down_revision: Union[str, Sequence[str], None] = "d4a7f9c2e610"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tickets",
        sa.Column(
            "progress",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )
    op.add_column(
        "tickets",
        sa.Column("work_notes", sa.Text(), nullable=True),
    )
    op.add_column(
        "tickets",
        sa.Column("evidence", sa.String(length=4000), nullable=True),
    )
    op.add_column(
        "tickets",
        sa.Column(
            "result",
            sa.String(length=4000),
            nullable=True,
        ),
    )
    op.add_column(
        "tickets",
        sa.Column(
            "version",
            sa.Integer(),
            server_default="1",
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_tickets_progress",
        "tickets",
        "progress >= 0 AND progress <= 100",
    )
    op.create_check_constraint(
        "ck_tickets_version",
        "tickets",
        "version >= 1",
    )

    op.add_column(
        "ticket_history",
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("ticket_history", "details")
    op.drop_constraint(
        "ck_tickets_version",
        "tickets",
        type_="check",
    )
    op.drop_constraint(
        "ck_tickets_progress",
        "tickets",
        type_="check",
    )
    op.drop_column("tickets", "version")
    op.drop_column("tickets", "result")
    op.drop_column("tickets", "evidence")
    op.drop_column("tickets", "work_notes")
    op.drop_column("tickets", "progress")
