
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.exceptions import ResourceConflictError
from src.domain.models.alert import Alert
from src.domain.models.alert_rule import AlertRule
from src.domain.models.node_monitoring import evaluate_node_monitoring
from src.domain.repositories.alert_repository import AlertRepository
from src.domain.repositories.server_repository import ServerRepository
from src.domain.repositories.telemetry_repository import TelemetryRepository


class AlertDetector:
    """
    Đánh giá Telemetry và trạng thái kết nối Node để phát hiện Alert.

    Quy tắc:
    - CPU/RAM/Disk chỉ được đánh giá khi dữ liệu còn fresh.
    - Node offline được đánh giá dựa trên thời điểm nhận Telemetry cuối.
    - Mỗi Node + Rule chỉ có một Alert đang hoạt động.
    - Alert đang hoạt động được phục hồi khi recovery condition thỏa mãn.
    """

    ACTIVE_STATUSES = {
        "FIRING",
        "ACKNOWLEDGED",
    }

    def __init__(
        self,
        alert_repository: AlertRepository,
        telemetry_repository: TelemetryRepository,
        server_repository: ServerRepository,
        stale_after_seconds: int = 30,
        offline_after_seconds: int = 90,
    ):
        if (
            isinstance(stale_after_seconds, bool)
            or not isinstance(stale_after_seconds, int)
            or stale_after_seconds <= 0
        ):
            raise ValueError(
                "stale_after_seconds phải là số nguyên dương."
            )

        if (
            isinstance(offline_after_seconds, bool)
            or not isinstance(offline_after_seconds, int)
            or offline_after_seconds <= 0
        ):
            raise ValueError(
                "offline_after_seconds phải là số nguyên dương."
            )

        if offline_after_seconds <= stale_after_seconds:
            raise ValueError(
                "offline_after_seconds phải lớn hơn stale_after_seconds."
            )

        self._alert_repository = alert_repository
        self._telemetry_repository = telemetry_repository
        self._server_repository = server_repository
        self._stale_after_seconds = stale_after_seconds
        self._offline_after_seconds = offline_after_seconds

    # ---------------------------------------------------------
    # Comparison
    # ---------------------------------------------------------

    @staticmethod
    def _matches(
        value: float,
        operator: str,
        threshold: float,
    ) -> bool:
        if operator == ">":
            return value > threshold

        if operator == ">=":
            return value >= threshold

        if operator == "<":
            return value < threshold

        if operator == "<=":
            return value <= threshold

        return False

    # ---------------------------------------------------------
    # Metric extraction
    # ---------------------------------------------------------

    def _get_metric_value(
        self,
        rule: AlertRule,
        telemetry,
        monitoring,
    ) -> float | None:
        if rule.metric == "node_offline_seconds":
            if monitoring.connection_status == "never_seen":
                return None

            elapsed = monitoring.seconds_since_received

            if elapsed is None or elapsed < 0:
                return None

            return float(elapsed)

        # Không sử dụng dữ liệu thiếu, stale hoặc thời gian không hợp lệ.
        if telemetry is None:
            return None

        if monitoring.data_status != "fresh":
            return None

        metric_values = {
            "cpu_percent": telemetry.cpu_percent,
            "memory_percent": telemetry.memory_percent,
            "disk_percent": telemetry.disk_percent,
        }

        value = metric_values.get(rule.metric)

        if value is None:
            return None

        return float(value)

    # ---------------------------------------------------------
    # Alert creation
    # ---------------------------------------------------------

    @staticmethod
    def _build_message(
        rule: AlertRule,
        value: float,
    ) -> str:
        if rule.metric == "node_offline_seconds":
            return (
                f"Node không gửi Telemetry trong "
                f"{value:.1f} giây. "
                f"Ngưỡng cấu hình: {rule.operator} {rule.threshold} giây."
            )

        return (
            f"{rule.metric} đạt {value:.2f}%, "
            f"vượt điều kiện {rule.operator} {rule.threshold}%."
        )

    def _create_alert(
        self,
        node_id: str,
        rule: AlertRule,
        value: float,
        now: datetime,
    ) -> bool:
        alert = Alert(
            id=str(uuid4()),
            node_id=node_id,
            rule_id=rule.id,
            metric=rule.metric,
            operator=rule.operator,
            threshold=rule.threshold,
            severity=rule.severity,
            status="FIRING",
            message=self._build_message(rule, value),
            triggered_at=now,
            acknowledged_at=None,
            recovered_at=None,
        )

        try:
            self._alert_repository.save(alert)
            return True

        except ResourceConflictError:
            # Worker khác có thể đã tạo Alert cho Node + Rule.
            # Không tạo bản ghi trùng.
            existing = (
                self._alert_repository.find_active_by_node_and_rule(
                    node_id,
                    rule.id,
                )
            )

            if existing is not None:
                return False

            # Xung đột không phải do Alert trùng thì không được
            # âm thầm bỏ qua lỗi.
            raise

    # ---------------------------------------------------------
    # Alert recovery
    # ---------------------------------------------------------

    def _recover_if_needed(
        self,
        alert: Alert,
        rule: AlertRule,
        value: float,
        now: datetime,
    ) -> bool:
        if (
            rule.recovery_operator is None
            or rule.recovery_threshold is None
        ):
            return False

        recovered = self._matches(
            value,
            rule.recovery_operator,
            rule.recovery_threshold,
        )

        if not recovered:
            return False

        updated = self._alert_repository.recover(
            alert.id,
            now,
        )

        return updated is not None

    # ---------------------------------------------------------
    # Evaluate one rule
    # ---------------------------------------------------------

    def _evaluate_rule(
        self,
        node_id: str,
        rule: AlertRule,
        telemetry,
        monitoring,
        now: datetime,
    ) -> str:
        value = self._get_metric_value(
            rule,
            telemetry,
            monitoring,
        )

        # Không có bằng chứng hợp lệ thì không tạo Alert
        # và cũng không phục hồi Alert đang tồn tại.
        if value is None:
            return "skipped"

        active_alert = (
            self._alert_repository.find_active_by_node_and_rule(
                node_id,
                rule.id,
            )
        )

        if active_alert is not None:
            if self._recover_if_needed(
                active_alert,
                rule,
                value,
                now,
            ):
                return "recovered"

            return "unchanged"

        triggered = self._matches(
            value,
            rule.operator,
            rule.threshold,
        )

        if not triggered:
            return "unchanged"

        created = self._create_alert(
            node_id,
            rule,
            value,
            now,
        )

        return "created" if created else "unchanged"

    # ---------------------------------------------------------
    # Evaluate one Node
    # ---------------------------------------------------------

    def evaluate_node(
        self,
        node_id: str,
        rules: list[AlertRule] | None = None,
        now: datetime | None = None,
    ) -> dict:
        if now is None:
            now = datetime.now(timezone.utc)

        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError(
                "now phải là datetime có timezone."
            )

        now = now.astimezone(timezone.utc)

        if rules is None:
            rules = self._alert_repository.list_active_rules()

        telemetry = self._telemetry_repository.get_latest(node_id)

        last_received_at = (
            self._telemetry_repository.get_last_received_at(node_id)
        )

        last_measured_at = (
            telemetry.measured_at
            if telemetry is not None
            else None
        )

        monitoring = evaluate_node_monitoring(
            now=now,
            last_received_at=last_received_at,
            last_measured_at=last_measured_at,
            stale_after_seconds=self._stale_after_seconds,
            offline_after_seconds=self._offline_after_seconds,
        )

        result = {
            "node_id": node_id,
            "created": 0,
            "recovered": 0,
            "unchanged": 0,
            "skipped": 0,
        }

        for rule in rules:
            if not rule.is_active:
                continue

            status = self._evaluate_rule(
                node_id=node_id,
                rule=rule,
                telemetry=telemetry,
                monitoring=monitoring,
                now=now,
            )

            result[status] += 1

        return result

    # ---------------------------------------------------------
    # Evaluate all Nodes
    # ---------------------------------------------------------

    def run_cycle(
        self,
        now: datetime | None = None,
    ) -> dict:
        if now is None:
            now = datetime.now(timezone.utc)

        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError(
                "now phải là datetime có timezone."
            )

        now = now.astimezone(timezone.utc)

        rules = self._alert_repository.list_active_rules()
        nodes = self._server_repository.list_servers()

        total = {
            "nodes_checked": 0,
            "created": 0,
            "recovered": 0,
            "unchanged": 0,
            "skipped": 0,
        }

        for node in nodes:
            node_id = str(node.id)

            result = self.evaluate_node(
                node_id=node_id,
                rules=rules,
                now=now,
            )

            total["nodes_checked"] += 1

            for key in (
                "created",
                "recovered",
                "unchanged",
                "skipped",
            ):
                total[key] += result[key]

        return total
