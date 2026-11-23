"""add agent registry

Revision ID: b7c4e2a19d6f
Revises: 8a91c4d2e5f0
Create Date: 2026-11-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b7c4e2a19d6f"
down_revision: Union[str, Sequence[str], None] = "8a91c4d2e5f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=128),
            nullable=False,
        ),
        sa.Column(
            "certificate_fingerprint",
            sa.String(length=64),
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
            "btrim(name) <> ''",
            name="ck_agents_name_not_blank",
        ),
        sa.CheckConstraint(
            "length(certificate_fingerprint) = 64",
            name="ck_agents_fingerprint_length",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "certificate_fingerprint",
            name="uq_agents_certificate_fingerprint",
        ),
    )

    op.create_table(
        "agent_node_access",
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.Column(
            "node_id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["node_id"],
            ["nodes.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "agent_id",
            "node_id",
        ),
    )

    op.create_index(
        "ix_agent_node_access_node_id",
        "agent_node_access",
        ["node_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_agent_node_access_node_id",
        table_name="agent_node_access",
    )

    op.drop_table("agent_node_access")
    op.drop_table("agents")