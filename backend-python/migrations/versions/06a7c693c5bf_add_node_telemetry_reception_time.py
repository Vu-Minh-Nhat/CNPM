"""Add Node telemetry reception time."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "06a7c693c5bf"
down_revision: Union[str, Sequence[str], None] = "1663b308482e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "nodes",
        sa.Column(
            "last_telemetry_received_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Khởi tạo từ thời điểm tiếp nhận lớn nhất đã lưu.
    # Node chưa có telemetry tiếp tục giữ NULL.
    op.execute(sa.text("""
        UPDATE nodes AS n
        SET last_telemetry_received_at = t.last_received_at
        FROM (
            SELECT
                node_id,
                MAX(received_at) AS last_received_at
            FROM node_telemetry
            GROUP BY node_id
        ) AS t
        WHERE n.id = t.node_id
          AND n.last_telemetry_received_at IS NULL
    """))


def downgrade() -> None:
    op.drop_column(
        "nodes",
        "last_telemetry_received_at",
    )