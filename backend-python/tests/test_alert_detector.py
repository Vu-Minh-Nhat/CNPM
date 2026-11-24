from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
import pytest

from src.services.alert_detector_service import (
    AlertDetectorService,
    AlertRule,
    AlertRuleManager,
    TelemetrySample,
)


def make_detector(threshold: float = 80.0, recovery: float = 70.0) -> tuple[AlertRuleManager, AlertDetectorService]:
    mgr = AlertRuleManager()
    mgr.upsert_rule(
        AlertRule(
            id="rule-cpu",
            name="High CPU",
            metric="cpu",
            threshold=threshold,
            recovery_threshold=recovery,
            enabled=True,
            stale_after_seconds=30,
            offline_after_seconds=90,
        ),
        actor_role="admin",
    )
    return mgr, AlertDetectorService(mgr)


def test_before_at_after_threshold_and_recovery():
    _, det = make_detector(threshold=80.0, recovery=70.0)
    t0 = datetime(2026, 11, 25, 1, 0, 0, tzinfo=timezone.utc)

    # Trước ngưỡng (79.9%) -> không có cảnh báo
    assert det.ingest_telemetry(TelemetrySample("node-1", t0, {"cpu": 79.9}), now=t0) == []

    # Tại ngưỡng (80.0%) -> tạo 1 cảnh báo active
    t1 = t0 + timedelta(seconds=10)
    alerts_t1 = det.ingest_telemetry(TelemetrySample("node-1", t1, {"cpu": 80.0}), now=t1)
    assert len(alerts_t1) == 1
    assert alerts_t1[0].status == "active"
    alert_id = alerts_t1[0].alert_id

    # Sau ngưỡng (92.0%) -> cập nhật cùng cảnh báo, không tạo trùng
    t2 = t0 + timedelta(seconds=20)
    alerts_t2 = det.ingest_telemetry(TelemetrySample("node-1", t2, {"cpu": 92.0}), now=t2)
    assert len(alerts_t2) == 1
    assert alerts_t2[0].alert_id == alert_id
    assert alerts_t2[0].status == "active"
    assert alerts_t2[0].hit_count == 2

    # Phục hồi (<= 70.0%) -> chuyển resolved
    t3 = t0 + timedelta(seconds=30)
    alerts_t3 = det.ingest_telemetry(TelemetrySample("node-1", t3, {"cpu": 68.0}), now=t3)
    assert len(alerts_t3) == 1
    assert alerts_t3[0].alert_id == alert_id
    assert alerts_t3[0].status == "resolved"


def test_missing_or_stale_data_not_zero_and_no_recovery():
    _, det = make_detector(threshold=80.0, recovery=70.0)
    t0 = datetime(2026, 11, 25, 1, 0, 0, tzinfo=timezone.utc)

    # Kích hoạt cảnh báo CPU
    a = det.ingest_telemetry(TelemetrySample("node-1", t0, {"cpu": 85.0}), now=t0)[0]
    assert a.status == "active"

    # Metric bị thiếu (None) ở thời điểm t0 + 5s -> không coi là 0, không phục hồi
    t1 = t0 + timedelta(seconds=5)
    assert det.ingest_telemetry(TelemetrySample("node-1", t1, {"cpu": None}), now=t1) == []
    assert det._alerts[("node-1", "rule:rule-cpu")].status == "active"

    # Mẫu cũ (quá stale_after_seconds=30s) -> bỏ qua
    t2 = t0 + timedelta(seconds=40)
    stale_sample = TelemetrySample("node-1", t0, {"cpu": 10.0})
    assert det.ingest_telemetry(stale_sample, now=t2) == []
    assert det._alerts[("node-1", "rule:rule-cpu")].status == "active"


def test_node_never_sent_vs_stopped_over_90s():
    _, det = make_detector()
    t0 = datetime(2026, 11, 25, 1, 0, 0, tzinfo=timezone.utc)

    # node-never-sent chưa từng gửi -> poller không tạo node_offline
    assert det.check_node_connectivity(now=t0 + timedelta(seconds=200)) == []

    # node-1 gửi lúc t0, sau đó ngừng
    det.ingest_telemetry(TelemetrySample("node-1", t0, {"cpu": 40.0}), now=t0)
    assert det.check_node_connectivity(now=t0 + timedelta(seconds=90)) == []

    # Quá 90s (ví dụ 95s) -> tạo cảnh báo node_offline
    offline_alerts = det.check_node_connectivity(now=t0 + timedelta(seconds=95))
    assert len(offline_alerts) == 1
    assert offline_alerts[0].alert_type == "node_offline"
    assert offline_alerts[0].status == "active"


def test_replay_and_concurrent_ingestion():
    _, det = make_detector(threshold=80.0, recovery=70.0)
    t0 = datetime(2026, 11, 25, 1, 0, 0, tzinfo=timezone.utc)

    def send_batch(i: int):
        ts = t0 + timedelta(seconds=i + 1)
        val = 90.0 if i % 2 == 0 else 50.0
        msg = TelemetrySample("node-c", ts, {"cpu": val}, message_id=f"msg-{i}")
        det.ingest_telemetry(msg, now=ts)
        # Gửi lại bản tin cũ
        det.ingest_telemetry(msg, now=ts + timedelta(seconds=1))

    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(send_batch, range(12)))

    # Không có lỗi race condition và trạng thái cuối nhất quán theo mốc thời gian mới nhất (i=11 -> cpu=50.0 -> resolved)
    rec = det._alerts[("node-c", "rule:rule-cpu")]
    assert rec.status == "resolved"