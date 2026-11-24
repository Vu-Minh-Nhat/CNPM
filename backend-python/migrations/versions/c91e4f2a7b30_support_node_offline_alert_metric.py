"""support node offline alert metric

Revision ID: c91e4f2a7b30
Revises: b7c4e2a19d6f
Create Date: 2026-11-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c91e4f2a7b30"
down_revision: Union[str, Sequence[str], None] = "b7c4e2a19d6f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


METRIC_CHECK = """
metric IN (
    'cpu_percent',
    'memory_percent',
    'disk_percent',
    'node_offline_seconds'
)
"""

RULE_THRESHOLD_CHECK = """
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
"""

RULE_RECOVERY_THRESHOLD_CHECK = """
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
"""

ALERT_THRESHOLD_CHECK = """
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
"""


def upgrade() -> None:
    # Alert rules
    op.drop_constraint(
        "ck_alert_rules_metric",
        "alert_rules",
        type_="check",
    )
    op.drop_constraint(
        "ck_alert_rules_threshold",
        "alert_rules",
        type_="check",
    )
    op.drop_constraint(
        "ck_alert_rules_recovery_threshold",
        "alert_rules",
        type_="check",
    )

    op.create_check_constraint(
        "ck_alert_rules_metric",
        "alert_rules",
        METRIC_CHECK,
    )
    op.create_check_constraint(
        "ck_alert_rules_threshold",
        "alert_rules",
        RULE_THRESHOLD_CHECK,
    )
    op.create_check_constraint(
        "ck_alert_rules_recovery_threshold",
        "alert_rules",
        RULE_RECOVERY_THRESHOLD_CHECK,
    )

    # Alerts
    op.drop_constraint(
        "ck_alerts_metric",
        "alerts",
        type_="check",
    )
    op.drop_constraint(
        "ck_alerts_threshold",
        "alerts",
        type_="check",
    )

    op.create_check_constraint(
        "ck_alerts_metric",
        "alerts",
        METRIC_CHECK,
    )
    op.create_check_constraint(
        "ck_alerts_threshold",
        "alerts",
        ALERT_THRESHOLD_CHECK,
    )


def downgrade() -> None:
    bind = op.get_bind()

    # Không cho downgrade nếu đã có Alert/Rule dùng metric mới.
    rule_count = bind.execute(
        sa.text(
            "SELECT count(*) FROM alert_rules "
            "WHERE metric = 'node_offline_seconds'"
        )
    ).scalar_one()

    alert_count = bind.execute(
        sa.text(
            "SELECT count(*) FROM alerts "
            "WHERE metric = 'node_offline_seconds'"
        )
    ).scalar_one()

    if rule_count or alert_count:
        raise RuntimeError(
            "Không thể downgrade: database đang có Rule hoặc Alert "
            "dùng metric node_offline_seconds."
        )

    op.drop_constraint(
        "ck_alert_rules_metric",
        "alert_rules",
        type_="check",
    )
    op.drop_constraint(
        "ck_alert_rules_threshold",
        "alert_rules",
        type_="check",
    )
    op.drop_constraint(
        "ck_alert_rules_recovery_threshold",
        "alert_rules",
        type_="check",
    )

    op.create_check_constraint(
        "ck_alert_rules_metric",
        "alert_rules",
        """
        metric IN ('cpu_percent', 'memory_percent', 'disk_percent')
        """,
    )
    op.create_check_constraint(
        "ck_alert_rules_threshold",
        "alert_rules",
        "threshold >= 0 AND threshold <= 100",
    )
    op.create_check_constraint(
        "ck_alert_rules_recovery_threshold",
        "alert_rules",
        """
        recovery_threshold IS NULL
        OR (
            recovery_threshold >= 0
            AND recovery_threshold <= 100
        )
        """,
    )

    op.drop_constraint(
        "ck_alerts_metric",
        "alerts",
        type_="check",
    )
    op.drop_constraint(
        "ck_alerts_threshold",
        "alerts",
        type_="check",
    )

    op.create_check_constraint(
        "ck_alerts_metric",
        "alerts",
        """
        metric IN ('cpu_percent', 'memory_percent', 'disk_percent')
        """,
    )
    op.create_check_constraint(
        "ck_alerts_threshold",
        "alerts",
        """
        threshold IS NULL
        OR (threshold >= 0 AND threshold <= 100)
        """,
    )
