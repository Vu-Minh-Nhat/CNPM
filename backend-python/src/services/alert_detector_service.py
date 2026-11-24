from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple
import threading

SUPPORTED_METRICS = {"cpu", "ram", "disk"}
DEFAULT_OFFLINE_SECONDS = 90


@dataclass
class AlertRule:
    id: str
    name: str
    metric: str
    threshold: float
    recovery_threshold: float
    enabled: bool = True
    stale_after_seconds: int = 30
    offline_after_seconds: int = DEFAULT_OFFLINE_SECONDS


@dataclass
class TelemetrySample:
    node_id: str
    timestamp: datetime
    metrics: Dict[str, Optional[float]]
    message_id: Optional[str] = None


@dataclass
class AlertRecord:
    alert_id: str
    node_id: str
    rule_id: str
    alert_type: str  # "threshold" | "node_offline"
    status: str      # "active" | "resolved"
    value: Optional[float]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_reason: Optional[str] = None
    hit_count: int = 1


RuleChangeCallback = Callable[[str, bool, Optional[AlertRule], Optional[datetime]], List[AlertRecord]]


class AlertRuleManager:
    def __init__(self, on_rule_changed: Optional[RuleChangeCallback] = None) -> None:
        self._rules: Dict[str, AlertRule] = {}
        self._lock = threading.RLock()
        self._on_rule_changed = on_rule_changed

    def set_rule_change_callback(self, callback: Optional[RuleChangeCallback]) -> None:
        with self._lock:
            self._on_rule_changed = callback

    def validate_rule(self, rule: AlertRule) -> None:
        if rule.metric not in SUPPORTED_METRICS:
            raise ValueError(f"Unsupported metric: {rule.metric}")
        if not (0.0 <= rule.threshold <= 100.0):
            raise ValueError("Threshold must be between 0 and 100")
        if not (0.0 <= rule.recovery_threshold <= 100.0):
            raise ValueError("Recovery threshold must be between 0 and 100")
        if rule.recovery_threshold >= rule.threshold:
            raise ValueError("Recovery threshold must be lower than threshold")
        if rule.stale_after_seconds <= 0 or rule.offline_after_seconds <= 0:
            raise ValueError("Time windows must be positive")

    def upsert_rule(
        self,
        rule: AlertRule,
        actor_role: str,
        now: Optional[datetime] = None,
    ) -> AlertRule:
        if actor_role not in {"admin", "operator"}:
            raise PermissionError("Insufficient permission to manage alert rules")
        self.validate_rule(rule)
        with self._lock:
            self._rules[rule.id] = rule
            cb = self._on_rule_changed
        if cb is not None:
            cb(rule.id, rule.enabled, rule, now)
        return rule

    def set_enabled(
        self,
        rule_id: str,
        enabled: bool,
        actor_role: str,
        now: Optional[datetime] = None,
    ) -> AlertRule:
        if actor_role not in {"admin", "operator"}:
            raise PermissionError("Insufficient permission to toggle alert rules")
        with self._lock:
            if rule_id not in self._rules:
                raise KeyError(f"Rule not found: {rule_id}")
            rule = self._rules[rule_id]
            rule.enabled = enabled
            cb = self._on_rule_changed
        if cb is not None:
            cb(rule_id, enabled, rule, now)
        return rule

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        with self._lock:
            return self._rules.get(rule_id)

    def list_rules(self) -> List[AlertRule]:
        with self._lock:
            return list(self._rules.values())


class AlertDetectorService:
    def __init__(self, rule_manager: AlertRuleManager) -> None:
        self.rule_manager = rule_manager
        self._lock = threading.RLock()
        self._last_seen_at: Dict[str, datetime] = {}
        self._last_sample_ts: Dict[str, datetime] = {}
        self._seen_messages: Dict[str, set] = {}
        # Key: (node_id, alert_key) -> AlertRecord
        self._alerts: Dict[Tuple[str, str], AlertRecord] = {}
        self._seq = 0
        self.rule_manager.set_rule_change_callback(self._handle_rule_changed)

    def _next_id(self) -> str:
        self._seq += 1
        return f"ALT-{self._seq:06d}"

    def _handle_rule_changed(
        self,
        rule_id: str,
        enabled: bool,
        rule: Optional[AlertRule],
        now: Optional[datetime] = None,
    ) -> List[AlertRecord]:
        ts = now or datetime.now(timezone.utc)
        if not enabled or rule is None:
            return self.resolve_alerts_for_disabled_rule(rule_id, now=ts)
        return self._reconcile_active_alerts_for_rule(rule, now=ts)

    def resolve_alerts_for_disabled_rule(
        self,
        rule_id: str,
        now: Optional[datetime] = None,
    ) -> List[AlertRecord]:
        now = now or datetime.now(timezone.utc)
        changed: List[AlertRecord] = []
        alert_key = f"rule:{rule_id}"
        with self._lock:
            for (_, key), alert in self._alerts.items():
                if key == alert_key and alert.status == "active":
                    alert.status = "resolved"
                    alert.resolved_at = now
                    alert.updated_at = now
                    alert.resolution_reason = "rule_disabled"
                    changed.append(alert)
        return changed

    def _reconcile_active_alerts_for_rule(
        self,
        rule: AlertRule,
        now: datetime,
    ) -> List[AlertRecord]:
        changed: List[AlertRecord] = []
        alert_key = f"rule:{rule.id}"
        with self._lock:
            for (_, key), alert in self._alerts.items():
                if key == alert_key and alert.status == "active":
                    if alert.value is not None and alert.value <= rule.recovery_threshold:
                        alert.status = "resolved"
                        alert.resolved_at = now
                        alert.updated_at = now
                        alert.resolution_reason = "rule_threshold_updated"
                        changed.append(alert)
        return changed

    def ingest_telemetry(
        self,
        sample: TelemetrySample,
        now: Optional[datetime] = None,
    ) -> List[AlertRecord]:
        now = now or datetime.now(timezone.utc)
        changed: List[AlertRecord] = []

        with self._lock:
            node_msgs = self._seen_messages.setdefault(sample.node_id, set())
            if sample.message_id and sample.message_id in node_msgs:
                # Bản tin gửi lại -> bỏ qua, không làm sai trạng thái
                return []

            prev_ts = self._last_sample_ts.get(sample.node_id)
            if prev_ts is not None and sample.timestamp <= prev_ts:
                # Mẫu đến muộn hoặc trùng mốc thời gian -> bỏ qua
                return []

            if sample.message_id:
                node_msgs.add(sample.message_id)
            self._last_sample_ts[sample.node_id] = sample.timestamp
            self._last_seen_at[sample.node_id] = max(now, sample.timestamp)

            # Node đã có telemetry mới quay lại -> đóng cảnh báo mất kết nối nếu đang active
            offline_key = (sample.node_id, "node_offline")
            offline_alert = self._alerts.get(offline_key)
            if offline_alert and offline_alert.status == "active":
                offline_alert.status = "resolved"
                offline_alert.resolved_at = now
                offline_alert.updated_at = now
                offline_alert.resolution_reason = "telemetry_resumed"
                changed.append(offline_alert)

            for rule in self.rule_manager.list_rules():
                alert_key = f"rule:{rule.id}"
                active = self._alerts.get((sample.node_id, alert_key))

                if not rule.enabled:
                    if active and active.status == "active":
                        active.status = "resolved"
                        active.resolved_at = now
                        active.updated_at = now
                        active.resolution_reason = "rule_disabled"
                        changed.append(active)
                    continue

                raw_val = sample.metrics.get(rule.metric)
                age_seconds = (now - sample.timestamp).total_seconds()
                is_valid_fresh = (
                    raw_val is not None
                    and isinstance(raw_val, (int, float))
                    and not isinstance(raw_val, bool)
                    and age_seconds <= rule.stale_after_seconds
                )

                # Dữ liệu thiếu hoặc cũ: không coi là 0 và không dùng để phục hồi
                if not is_valid_fresh:
                    continue

                val = float(raw_val)
                if val >= rule.threshold:
                    if active is None or active.status != "active":
                        rec = AlertRecord(
                            alert_id=self._next_id(),
                            node_id=sample.node_id,
                            rule_id=rule.id,
                            alert_type="threshold",
                            status="active",
                            value=val,
                            created_at=now,
                            updated_at=now,
                            hit_count=1,
                        )
                        self._alerts[(sample.node_id, alert_key)] = rec
                        changed.append(rec)
                    else:
                        active.value = val
                        active.updated_at = now
                        active.hit_count += 1
                        changed.append(active)
                elif val <= rule.recovery_threshold:
                    if active is not None and active.status == "active":
                        active.status = "resolved"
                        active.value = val
                        active.resolved_at = now
                        active.updated_at = now
                        active.resolution_reason = "recovered"
                        changed.append(active)

        return changed

    def check_node_connectivity(
        self,
        now: Optional[datetime] = None,
        offline_threshold_seconds: int = DEFAULT_OFFLINE_SECONDS,
    ) -> List[AlertRecord]:
        """Chạy định kỳ bởi worker; không phụ thuộc request ghi mới."""
        now = now or datetime.now(timezone.utc)
        changed: List[AlertRecord] = []

        with self._lock:
            # Chỉ kiểm tra các Node đã từng gửi telemetry (_last_seen_at),
            # không đánh đồng Node chưa từng gửi với Node ngừng gửi.
            for node_id, last_seen in self._last_seen_at.items():
                elapsed = (now - last_seen).total_seconds()
                key = (node_id, "node_offline")
                current = self._alerts.get(key)

                if elapsed > offline_threshold_seconds:
                    if current is None or current.status != "active":
                        rec = AlertRecord(
                            alert_id=self._next_id(),
                            node_id=node_id,
                            rule_id="system_node_offline",
                            alert_type="node_offline",
                            status="active",
                            value=elapsed,
                            created_at=now,
                            updated_at=now,
                            hit_count=1,
                        )
                        self._alerts[key] = rec
                        changed.append(rec)
                    else:
                        current.value = elapsed
                        current.updated_at = now
                        current.hit_count += 1
                        changed.append(current)

            # Đồng bộ cảnh báo threshold khi quy tắc bị sửa ngưỡng hoặc bị tắt
            for (_, alert_key), alert in list(self._alerts.items()):
                if alert.alert_type != "threshold" or alert.status != "active":
                    continue
                rule_id = alert_key.removeprefix("rule:")
                rule = self.rule_manager.get_rule(rule_id)
                if rule is None or not rule.enabled:
                    alert.status = "resolved"
                    alert.resolved_at = now
                    alert.updated_at = now
                    alert.resolution_reason = "rule_disabled_or_deleted"
                    changed.append(alert)
                elif alert.value is not None and alert.value <= rule.recovery_threshold:
                    alert.status = "resolved"
                    alert.resolved_at = now
                    alert.updated_at = now
                    alert.resolution_reason = "rule_threshold_updated"
                    changed.append(alert)

        return changed