from __future__ import annotations

import io
import pytest
from flask import Flask
from src.api.controllers.tickets_controller import create_tickets_blueprint
from src.repositories.ticket_repository import TicketAuditLogger, TicketRepository
from src.services.ticket_service import TicketService


@pytest.fixture()
def app_ctx(tmp_path):
    store_file = str(tmp_path / "tickets_store.json")
    repo = TicketRepository(store_path=store_file)
    audit = TicketAuditLogger(repo)
    service = TicketService(repo=repo, audit_logger=audit)
    app = Flask(__name__)
    app.register_blueprint(create_tickets_blueprint(service))
    return app.test_client(), repo, audit


def _headers(uid: str, role: str, nodes: str = ""):
    h = {"X-User-Id": uid, "X-User-Role": role}
    if nodes:
        h["X-Allowed-Nodes"] = nodes
    return h


def test_full_happy_path_and_alert_independence(app_ctx):
    client, repo, audit = app_ctx

    r = client.post(
        "/tickets",
        json={"title": "Kiểm tra quạt node-01", "node_id": "node-01", "alert_id": "ALT-1"},
        headers=_headers("u-op", "OPERATOR"),
    )
    assert r.status_code == 201
    ticket = r.get_json()
    tid = ticket["id"]
    assert ticket["status"] == "OPEN"

    r = client.post(
        f"/tickets/{tid}/assign",
        json={"assignee_id": "u-tech-1", "expected_version": ticket["version"]},
        headers=_headers("u-op", "OPERATOR"),
    )
    assert r.status_code == 200
    assert r.get_json()["status"] == "ASSIGNED"

    v = r.get_json()["version"]
    r = client.post(f"/tickets/{tid}/start", json={"expected_version": v}, headers=_headers("u-tech-1", "TECHNICIAN"))
    assert r.status_code == 200
    v = r.get_json()["version"]

    r = client.patch(
        f"/tickets/{tid}/work",
        json={"progress_pct": 80, "work_notes": "Đã thay quạt làm mát", "expected_version": v},
        headers=_headers("u-tech-1", "TECHNICIAN"),
    )
    assert r.status_code == 200
    v = r.get_json()["version"]

    r = client.post(
        f"/tickets/{tid}/evidences",
        data={"note": "Log nhiệt độ", "expected_version": str(v), "file": (io.BytesIO(b"log-data"), "proof.txt")},
        headers=_headers("u-tech-1", "TECHNICIAN"),
        content_type="multipart/form-data",
    )
    assert r.status_code == 201
    v = repo.get_ticket(tid)["version"]

    r = client.post(f"/tickets/{tid}/submit-review", json={"expected_version": v}, headers=_headers("u-tech-1", "TECHNICIAN"))
    assert r.status_code == 200
    assert r.get_json()["status"] == "PENDING_REVIEW"

    v = r.get_json()["version"]
    r = client.post(
        f"/tickets/{tid}/review",
        json={"decision": "approve", "result_summary": "Nhiệt độ node-01 ổn định", "expected_version": v},
        headers=_headers("u-op", "OPERATOR"),
    )
    assert r.status_code == 200
    assert r.get_json()["status"] == "CLOSED"
    assert repo._state["alerts"]["ALT-1"]["status"] == "active"

    detail = client.get(f"/tickets/{tid}", headers=_headers("u-op", "OPERATOR")).get_json()
    assert len(detail["history"]) >= 5
    assert any(e["event"] == "ticket_closed" for e in repo._state["audit_logs"])


def test_return_for_rework_requires_reason(app_ctx):
    client, _, _ = app_ctx
    t = client.post("/tickets", json={"title": "Fix disk", "node_id": "node-01"}, headers=_headers("u-op", "OPERATOR")).get_json()
    tid = t["id"]
    client.post(f"/tickets/{tid}/assign", json={"assignee_id": "u-tech-1"}, headers=_headers("u-op", "OPERATOR"))
    client.post(f"/tickets/{tid}/start", json={}, headers=_headers("u-tech-1", "TECHNICIAN"))
    client.post(f"/tickets/{tid}/submit-review", json={}, headers=_headers("u-tech-1", "TECHNICIAN"))

    bad = client.post(f"/tickets/{tid}/review", json={"decision": "reject"}, headers=_headers("u-op", "OPERATOR"))
    assert bad.status_code == 422

    ok = client.post(
        f"/tickets/{tid}/review",
        json={"decision": "reject", "reason": "Chưa đính kèm ảnh đo đạc"},
        headers=_headers("u-op", "OPERATOR"),
    )
    assert ok.status_code == 200
    assert ok.get_json()["status"] == "IN_PROGRESS"
    assert ok.get_json()["return_reason"] == "Chưa đính kèm ảnh đo đạc"


def test_conflict_evidence_limits_close_requirements_and_scope(app_ctx):
    client, _, _ = app_ctx
    t = client.post("/tickets", json={"title": "Kiểm tra PSU", "node_id": "node-01"}, headers=_headers("u-op", "OPERATOR")).get_json()
    tid = t["id"]

    # Xung đột version -> 409
    conflict = client.post(
        f"/tickets/{tid}/assign",
        json={"assignee_id": "u-tech-1", "expected_version": 999},
        headers=_headers("u-op", "OPERATOR"),
    )
    assert conflict.status_code == 409

    client.post(f"/tickets/{tid}/assign", json={"assignee_id": "u-tech-1"}, headers=_headers("u-op", "OPERATOR"))

    # Ngoài scope node -> 403
    assert client.get(f"/tickets/{tid}", headers=_headers("u-tech-1", "TECHNICIAN", nodes="node-02")).status_code == 403

    # Upload sai mime -> 415
    bad_mime = client.post(
        f"/tickets/{tid}/evidences",
        data={"file": (io.BytesIO(b"MZ..."), "malware.exe")},
        headers=_headers("u-tech-1", "TECHNICIAN"),
        content_type="multipart/form-data",
    )
    assert bad_mime.status_code == 415

    # Upload file > 10MB -> 413
    oversize = client.post(
        f"/tickets/{tid}/evidences",
        data={"file": (io.BytesIO(b"x" * (10 * 1024 * 1024 + 1)), "big.txt")},
        headers=_headers("u-tech-1", "TECHNICIAN"),
        content_type="multipart/form-data",
    )
    assert oversize.status_code == 413

    client.post(f"/tickets/{tid}/start", json={}, headers=_headers("u-tech-1", "TECHNICIAN"))
    client.post(f"/tickets/{tid}/submit-review", json={}, headers=_headers("u-tech-1", "TECHNICIAN"))

    # Đóng ticket thiếu result_summary -> 422
    no_result = client.post(
        f"/tickets/{tid}/review",
        json={"decision": "approve", "result_summary": ""},
        headers=_headers("u-op", "OPERATOR"),
    )
    assert no_result.status_code == 422

    # Đóng ticket thiếu bằng chứng/ghi chú -> 422
    no_evidence = client.post(
        f"/tickets/{tid}/review",
        json={"decision": "approve", "result_summary": "Nguồn hoạt động bình thường"},
        headers=_headers("u-op", "OPERATOR"),
    )
    assert no_evidence.status_code == 422