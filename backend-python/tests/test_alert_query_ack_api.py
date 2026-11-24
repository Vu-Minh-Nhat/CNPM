from datetime import datetime, timezone

import pytest
from flask import Blueprint

from src.api.controllers import alert_rules_controller
from src.create_app import create_app


@pytest.fixture
def client(monkeypatch):
    fresh_bp = Blueprint("alert_rules", __name__, url_prefix="/alert-rules")
    monkeypatch.setattr(alert_rules_controller, "alert_rules_bp", fresh_bp)

    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def _seed_alert(client, rule_id="rule-cpu-high", node_id="node-01", cpu_val=88.0):
    rule = {
        "id": rule_id,
        "name": "High CPU Rule",
        "metric": "cpu",
        "threshold": 70.0,
        "recovery_threshold": 50.0,
        "enabled": True,
        "stale_after_seconds": 30,
        "offline_after_seconds": 90,
    }
    res_rule = client.post("/alert-rules", json=rule, headers={"X-User-Role": "admin"})
    assert res_rule.status_code == 200

    payload = {
        "node_id": node_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {"cpu": cpu_val, "ram": 50.0, "disk": 40.0},
        "message_id": f"msg-{node_id}-{cpu_val}",
    }
    res_tel = client.post("/telemetry", json=payload)
    assert res_tel.status_code == 202

    res_alerts = client.get("/alerts")
    assert res_alerts.status_code == 200
    listed = res_alerts.get_json()
    assert listed is not None and len(listed["items"]) > 0
    return listed["items"][-1]["alert_id"]


def test_list_filter_and_pagination(client):
    _seed_alert(client, rule_id="r1", node_id="node-a", cpu_val=80.0)
    _seed_alert(client, rule_id="r2", node_id="node-b", cpu_val=95.0)

    res = client.get("/alerts?node_id=node-b&status=active&page=1&page_size=1")
    assert res.status_code == 200
    data = res.get_json()
    # node-b kích hoạt cả r1 lẫn r2 -> tổng 2 cảnh báo active, chia 2 trang với page_size=1
    assert data["total"] == 2
    assert data["total_pages"] == 2
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert len(data["items"]) == 1

    item = data["items"][0]
    assert item["node_id"] == "node-b"
    assert item["status"] == "active"
    assert item["value"] == 95.0
    assert item["threshold"] == 70.0
    assert item["reason"]
    assert item["created_at"]
    assert item["acknowledged"] is False


def test_detail_and_acknowledge_preserves_active_status_and_is_idempotent(client):
    alert_id = _seed_alert(client, rule_id="r-ack", node_id="node-ack", cpu_val=92.0)

    detail_before = client.get(f"/alerts/{alert_id}")
    assert detail_before.status_code == 200
    d0 = detail_before.get_json()
    assert d0["alert_id"] == alert_id
    assert d0["acknowledged"] is False
    assert any(log["action"] == "alert_created" for log in d0["audit_logs"])

    ack_1 = client.post(
        f"/alerts/{alert_id}/acknowledge",
        json={"note": "Đang kiểm tra tải CPU"},
        headers={"X-User-Role": "operator", "X-User-Id": "op-khoi"},
    )
    assert ack_1.status_code == 200
    d1 = ack_1.get_json()
    assert d1["acknowledged"] is True
    assert d1["acknowledged_by"] == "op-khoi"
    assert d1["acknowledged_at"] is not None
    assert d1["status"] == "active"
    assert d1["resolved_at"] is None
    assert d1["idempotent_replay"] is False
    assert any(log["action"] == "alert_acknowledged" for log in d1["audit_logs"])

    ack_2 = client.post(
        f"/alerts/{alert_id}/acknowledge",
        json={"note": "Gửi lại ack"},
        headers={"X-User-Role": "operator", "X-User-Id": "op-khoi"},
    )
    assert ack_2.status_code == 200
    d2 = ack_2.get_json()
    assert d2["acknowledged"] is True
    assert d2["acknowledged_at"] == d1["acknowledged_at"]
    assert d2["idempotent_replay"] is True
    ack_logs = [log for log in d2["audit_logs"] if log["action"] == "alert_acknowledged"]
    assert len(ack_logs) == 1


def test_permissions_401_403_404_and_no_delete_route(client, monkeypatch):
    alert_id = _seed_alert(client, rule_id="r-perm", node_id="node-perm", cpu_val=85.0)

    assert client.get("/alerts/ALT-999999").status_code == 404
    assert client.post("/alerts/ALT-999999/acknowledge", headers={"X-User-Role": "admin"}).status_code == 404

    forbidden = client.post(f"/alerts/{alert_id}/acknowledge", headers={"X-User-Role": "viewer"})
    assert forbidden.status_code == 403

    monkeypatch.setenv("ALERT_API_REQUIRE_AUTH", "true")
    assert client.get("/alerts").status_code == 401
    assert client.post(f"/alerts/{alert_id}/acknowledge").status_code == 401

    assert client.delete(f"/alerts/{alert_id}").status_code in (404, 405)