"""add marker management

Revision ID: 2e4fb41d32fd
Revises: 37ef391dbfde
Create Date: 2026-11-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "2e4fb41d32fd"
down_revision: Union[str, Sequence[str], None] = "37ef391dbfde"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create marker management storage."""

    op.create_table(
        "markers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "marker_type",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "identifier",
            sa.String(length=128),
            nullable=False,
        ),
        sa.Column(
            "node_id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
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
            "btrim(marker_type) <> ''",
            name="ck_markers_type_not_blank",
        ),
        sa.CheckConstraint(
            "btrim(identifier) <> ''",
            name="ck_markers_identifier_not_blank",
        ),
        sa.ForeignKeyConstraint(
            ["node_id"],
            ["nodes.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "marker_type",
            "identifier",
            name="uq_markers_type_identifier",
        ),
    )

    op.create_index(
        "ix_markers_node_id",
        "markers",
        ["node_id"],
    )

    op.create_index(
        "ix_markers_active_lookup",
        "markers",
        ["marker_type", "identifier", "is_active"],
    )


def downgrade() -> None:
    """Drop marker management storage."""

    op.drop_index(
        "ix_markers_active_lookup",
        table_name="markers",
    )

    op.drop_index(
        "ix_markers_node_id",
        table_name="markers",
    )

    op.drop_table("markers")