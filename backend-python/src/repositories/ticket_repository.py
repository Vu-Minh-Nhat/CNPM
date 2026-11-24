from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any


_SHARED_STORES: dict[str, dict[str, Any]] = {}
_LOCK = threading.Lock()


def _default_seed() -> dict[str, Any]:
    return {
        "seq": 0,
        "users": {
            "u-admin": {"id": "u-admin", "role": "ADMIN", "is_active": True},
            "u-op": {"id": "u-op", "role": "OPERATOR", "is_active": True},
            "u-tech-1": {"id": "u-tech-1", "role": "TECHNICIAN", "is_active": True},
            "u-tech-2": {"id": "u-tech-2", "role": "TECHNICIAN", "is_active": True},
            "u-tech-locked": {"id": "u-tech-locked", "role": "TECHNICIAN", "is_active": False},
            "u-viewer": {"id": "u-viewer", "role": "VIEWER", "is_active": True},
        },
        "nodes": {
            "node-01": {"id": "node-01", "name": "node-web-01"},
            "node-02": {"id": "node-02", "name": "node-web-02"},
        },
        "alerts": {
            "ALT-1": {"id": "ALT-1", "node_id": "node-01", "status": "active"},
            "ALT-2": {"id": "ALT-2", "node_id": "node-02", "status": "active"},
        },
        "tickets": {},
        "audit_logs": [],
    }


class TicketRepository:
    def __init__(self, store_path: str | None = None) -> None:
        env_path = store_path or os.environ.get("TICKET_STORE_PATH", "").strip()
        self.store_path = Path(env_path) if env_path else None
        key = str(self.store_path.resolve()) if self.store_path else "__default_memory__"
        with _LOCK:
            if self.store_path and self.store_path.exists():
                self._state = json.loads(self.store_path.read_text(encoding="utf-8"))
                _SHARED_STORES[key] = self._state
            elif key not in _SHARED_STORES:
                _SHARED_STORES[key] = _default_seed()
                self._state = _SHARED_STORES[key]
                self._persist()
            else:
                self._state = _SHARED_STORES[key]

    def _persist(self) -> None:
        if self.store_path:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            self.store_path.write_text(
                json.dumps(self._state, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def next_ticket_code(self) -> str:
        with _LOCK:
            self._state["seq"] += 1
            code = f"TKT-{self._state['seq']:06d}"
            self._persist()
            return code

    def get_user(self, uid: str) -> dict[str, Any] | None:
        return self._state["users"].get(uid)

    def get_node(self, nid: str) -> dict[str, Any] | None:
        return self._state["nodes"].get(nid)

    def get_alert(self, aid: str) -> dict[str, Any] | None:
        return self._state["alerts"].get(aid)

    def save_ticket(self, ticket: dict[str, Any]) -> None:
        with _LOCK:
            self._state["tickets"][ticket["id"]] = ticket
            self._persist()

    def get_ticket(self, tid: str) -> dict[str, Any] | None:
        return self._state["tickets"].get(tid)

    def list_tickets(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        items = list(self._state["tickets"].values())
        if filters.get("status"):
            items = [t for t in items if t["status"] == filters["status"]]
        if filters.get("node_id"):
            items = [t for t in items if t["node_id"] == filters["node_id"]]
        if filters.get("assignee_id"):
            items = [t for t in items if t.get("assignee_id") == filters["assignee_id"]]
        return items


class TicketAuditLogger:
    def __init__(self, repo: TicketRepository) -> None:
        self.repo = repo

    def record(self, **kwargs: Any) -> None:
        with _LOCK:
            self.repo._state.setdefault("audit_logs", []).append(kwargs)
            self.repo._persist()