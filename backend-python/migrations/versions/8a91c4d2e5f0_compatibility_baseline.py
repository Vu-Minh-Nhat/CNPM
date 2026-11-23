"""Compatibility baseline for the existing arimms_python_check database.

Revision ID: 8a91c4d2e5f0
Revises: 9826d73dbfbd

This revision adopts an existing database revision that was not
present in the current repository migration history.

It intentionally does not modify the database schema.
"""

from typing import Sequence, Union


revision: str = "8a91c4d2e5f0"
down_revision: Union[str, Sequence[str], None] = "9826d73dbfbd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adopt the existing database revision without schema changes."""
    pass


def downgrade() -> None:
    """No schema changes were performed by this revision."""
    pass
