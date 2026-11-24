
"""repair node telemetry reception time

Revision ID: 9826d73dbfbd
Revises: 2e4fb41d32fd
Create Date: 2026-11-22
"""

from typing import Sequence, Union

# Alembic revision identifiers.
revision: str = "9826d73dbfbd"
down_revision: Union[str, Sequence[str], None] = "2e4fb41d32fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    The column was already created by migration
    06a7c693c5bf_add_node_telemetry_reception_time.py.

    Keep this revision as a no-op to preserve the
    existing Alembic migration history.
    """
    pass


def downgrade() -> None:
    """
    The column belongs to migration 06a7c693c5bf.
    Do not drop it here.
    """
    pass
