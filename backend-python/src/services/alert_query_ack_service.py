from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

from src.services.alert_detector_service import AlertDetectorService, AlertRuleManager


class AlertApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso_dt(value: Optional[str], field_name: str) -> Optional[datetime]:
    if value is None or str(value).strip() == "":
        return None
    raw = str(value).strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise AlertApiError(400, "INVALID_TIMESTAMP", f"Invalid '{field_name}' timestamp: {value}") from exc
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _parse_bool_query(value: Optional[str], field_name: str) -> Optional[bool]:
    if value is None or str(value).strip() == "":
        return None
    lowered = str(value).strip().lower()
    if lowered in ("1", "true", "yes"):
        return True
    if lowered in ("0", "false", "no"):
        return False
    raise AlertApiError(400, "INVALID_BOOLEAN", f"Invalid boolean for '{field_name}': {value}")


def _infer_severity(alert_type: str, value: Optional[float], threshold: Optional[float]) -> str:
    if alert_type == "node_offline":
        return "critical"
    if value is not None and threshold is not None and threshold > 0:
        ratio = value / threshold
        if ratio >= 1.5 or value >= 90.0:
            return "critical"
        if ratio >= 1.15 or value >= 75.0:
            return "warning"
    return "warning"


def _build_reason(
    alert_type: str,
    rule: Any,
    node_id: str,
    value: Optional[float],
    threshold: Optional[float],
) -> str:
    if alert_type == "node_offline":
        offline_sec = getattr(rule, "offline_after_seconds", 90) if rule else 90
        return f"Node '{node_id}' has not sent telemetry for more than {offline_sec}s"
    metric = getattr(rule, "metric", "metric") if rule else "metric"
    if value is not None and threshold is not None:
        return f"{metric} value {value} exceeded threshold {threshold}"
    return f"Alert triggered on node '{node_id}'"


def _serialize_alert_obj(obj: Any) -> Dict[str, Any]:
    if isinstance(obj, dict):
        return dict(obj)
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return dict(obj.to_dict())
    data: Dict[str, Any] = {}
    for attr in (
        "alert_id",
        "id",
        "rule_id",
        "node_id",
        "alert_type",
        "status",
        "value",
        "hit_count",
        "created_at",
        "updated_at",
        "resolved_at",
        "resolution_reason",
    ):
        if hasattr(obj, attr):
            val = getattr(obj, attr)
            if isinstance(val, datetime):
                val = val.isoformat()
            data[attr] = val
    if "alert_id" not in data and "id" in data:
        data["alert_id"] = data["id"]
    return data


@dataclass
class AlertAckRecord:
    alert_id: str
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    audit_logs: List[Dict[str, Any]] = field(default_factory=list)


class AlertQueryAckService:
    ACK_ALLOWED_ROLES = {"admin", "operator", "engineer", "oncall"}
    READ_ALLOWED_ROLES = {"admin", "operator", "engineer", "oncall", "viewer"}

    def __init__(
        self,
        detector: AlertDetectorService,
        rule_manager: AlertRuleManager,
    ) -> None:
        self.detector = detector
        self.rule_manager = rule_manager
        self._lock = RLock()
        self._ack_by_alert: Dict[str, AlertAckRecord] = {}
        self._seen_alert_states: Dict[str, Tuple[str, int, Optional[str]]] = {}

    @staticmethod
    def resolve_actor(headers: Dict[str, str], require_auth: bool = False) -> Tuple[str, str]:
        normalized = {k.lower(): v.strip() for k, v in headers.items() if v and v.strip()}
        auth_header = normalized.get("authorization", "")
        role_header = normalized.get("x-user-role", "")
        user_header = normalized.get("x-user-id") or normalized.get("x-actor") or ""

        if require_auth and not auth_header and not role_header and not user_header:
            raise AlertApiError(401, "UNAUTHORIZED", "Missing authentication credentials")

        if not role_header and auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip().lower()
            if token in ("admin", "operator", "engineer", "oncall", "viewer"):
                role_header = token

        role = role_header.lower() if role_header else "operator"
        actor = user_header or (f"role:{role}" if role_header else "anonymous-operator")
        return actor, role

    def ensure_read_permission(self, headers: Dict[str, str], require_auth: bool = False) -> None:
        _, role = self.resolve_actor(headers, require_auth=require_auth)
        if role not in self.READ_ALLOWED_ROLES:
            raise AlertApiError(403, "FORBIDDEN", f"Role '{role}' is not allowed to query alerts")

    def ensure_ack_permission(self, headers: Dict[str, str], require_auth: bool = True) -> Tuple[str, str]:
        actor, role = self.resolve_actor(headers, require_auth=require_auth)
        if role not in self.ACK_ALLOWED_ROLES:
            raise AlertApiError(403, "FORBIDDEN", f"Role '{role}' is not allowed to acknowledge alerts")
        return actor, role

    def _get_raw_alerts(self) -> List[Dict[str, Any]]:
        detector_lock = getattr(self.detector, "_lock", None)
        if detector_lock is not None:
            with detector_lock:
                raw_dict = getattr(self.detector, "_alerts", None)
                if isinstance(raw_dict, dict):
                    return [_serialize_alert_obj(x) for x in raw_dict.values()]
        else:
            raw_dict = getattr(self.detector, "_alerts", None)
            if isinstance(raw_dict, dict):
                return [_serialize_alert_obj(x) for x in raw_dict.values()]
        return []

    def _sync_records_locked(self) -> List[Dict[str, Any]]:
        raw_alerts = self._get_raw_alerts()
        rules_map = {r.id: r for r in self.rule_manager.list_rules()}
        now_iso = _utc_now().isoformat()

        enriched: List[Dict[str, Any]] = []
        for item in raw_alerts:
            alert_id = str(item.get("alert_id"))
            rule_id = item.get("rule_id")
            node_id = str(item.get("node_id", ""))
            alert_type = str(item.get("alert_type", "threshold"))
            status = str(item.get("status", "active"))
            value = item.get("value")
            hit_count = int(item.get("hit_count", 1))
            resolution_reason = item.get("resolution_reason")

            rule = rules_map.get(rule_id) if rule_id else None
            threshold = getattr(rule, "threshold", None) if rule else None

            rec = self._ack_by_alert.get(alert_id)
            if rec is None:
                rec = AlertAckRecord(
                    alert_id=alert_id,
                    audit_logs=[
                        {
                            "action": "alert_created",
                            "actor": "system:alert_detector",
                            "timestamp": item.get("created_at") or now_iso,
                            "detail": {
                                "status": status,
                                "alert_type": alert_type,
                                "value": value,
                                "threshold": threshold,
                            },
                        }
                    ],
                )
                self._ack_by_alert[alert_id] = rec

            prev_state = self._seen_alert_states.get(alert_id)
            curr_state = (status, hit_count, resolution_reason)
            if prev_state is not None and prev_state != curr_state:
                prev_status, prev_hits, _ = prev_state
                if hit_count > prev_hits and status == "active":
                    rec.audit_logs.append(
                        {
                            "action": "alert_updated",
                            "actor": "system:alert_detector",
                            "timestamp": item.get("updated_at") or now_iso,
                            "detail": {"hit_count": hit_count, "value": value},
                        }
                    )
                if prev_status != "resolved" and status == "resolved":
                    rec.audit_logs.append(
                        {
                            "action": "alert_resolved",
                            "actor": "system:alert_detector",
                            "timestamp": item.get("resolved_at") or now_iso,
                            "detail": {"resolution_reason": resolution_reason},
                        }
                    )
            self._seen_alert_states[alert_id] = curr_state

            severity = _infer_severity(alert_type, value, threshold)
            reason = _build_reason(alert_type, rule, node_id, value, threshold)

            enriched.append(
                {
                    "alert_id": alert_id,
                    "rule_id": rule_id,
                    "node_id": node_id,
                    "alert_type": alert_type,
                    "severity": severity,
                    "status": status,
                    "reason": reason,
                    "value": value,
                    "threshold": threshold,
                    "hit_count": hit_count,
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                    "resolved_at": item.get("resolved_at"),
                    "resolution_reason": resolution_reason,
                    "acknowledged": rec.acknowledged,
                    "acknowledged_by": rec.acknowledged_by,
                    "acknowledged_at": rec.acknowledged_at.isoformat() if rec.acknowledged_at else None,
                }
            )
        return enriched

    def _get_alert_detail_locked(self, alert_id: str, items: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        synced = items if items is not None else self._sync_records_locked()
        matched = next((x for x in synced if x["alert_id"] == alert_id), None)
        if matched is None:
            raise AlertApiError(404, "ALERT_NOT_FOUND", f"Alert '{alert_id}' not found")
        rec = self._ack_by_alert[alert_id]
        return {
            **matched,
            "audit_logs": list(rec.audit_logs),
        }

    def list_alerts(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        node_id = (query_params.get("node_id") or "").strip() or None
        alert_type = (query_params.get("alert_type") or query_params.get("type") or "").strip() or None
        severity = (query_params.get("severity") or query_params.get("level") or "").strip().lower() or None
        status = (query_params.get("status") or "").strip().lower() or None
        ack_filter = _parse_bool_query(query_params.get("acknowledged"), "acknowledged")
        time_from = _parse_iso_dt(query_params.get("from") or query_params.get("start_time"), "from")
        time_to = _parse_iso_dt(query_params.get("to") or query_params.get("end_time"), "to")

        try:
            page = int(query_params.get("page", 1))
            page_size = int(query_params.get("page_size", 20))
        except (TypeError, ValueError) as exc:
            raise AlertApiError(400, "INVALID_PAGINATION", "page and page_size must be integers") from exc

        if page < 1 or page_size < 1 or page_size > 100:
            raise AlertApiError(400, "INVALID_PAGINATION", "page must be >= 1 and page_size between 1 and 100")

        with self._lock:
            items = self._sync_records_locked()

        filtered: List[Dict[str, Any]] = []
        for item in items:
            if node_id and item["node_id"] != node_id:
                continue
            if alert_type and item["alert_type"] != alert_type:
                continue
            if severity and item["severity"].lower() != severity:
                continue
            if status and item["status"].lower() != status:
                continue
            if ack_filter is not None and item["acknowledged"] is not ack_filter:
                continue

            item_dt = _parse_iso_dt(item.get("created_at"), "created_at")
            if item_dt is not None:
                if time_from is not None and item_dt < time_from:
                    continue
                if time_to is not None and item_dt > time_to:
                    continue

            filtered.append(item)

        total = len(filtered)
        total_pages = max(1, math.ceil(total / page_size)) if total > 0 else 1
        start = (page - 1) * page_size
        end = start + page_size

        return {
            "items": filtered[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    def get_alert_detail(self, alert_id: str) -> Dict[str, Any]:
        with self._lock:
            return self._get_alert_detail_locked(alert_id)

    def acknowledge_alert(
        self,
        alert_id: str,
        headers: Dict[str, str],
        body: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
    ) -> Dict[str, Any]:
        actor, role = self.ensure_ack_permission(headers, require_auth=require_auth)
        payload = body if isinstance(body, dict) else {}
        note = (payload.get("note") or "").strip() or None
        custom_actor = (payload.get("acknowledged_by") or "").strip()
        final_actor = custom_actor or actor

        with self._lock:
            items = self._sync_records_locked()
            matched = next((x for x in items if x["alert_id"] == alert_id), None)
            if matched is None:
                raise AlertApiError(404, "ALERT_NOT_FOUND", f"Alert '{alert_id}' not found")

            rec = self._ack_by_alert[alert_id]
            if rec.acknowledged:
                detail = self._get_alert_detail_locked(alert_id, items=items)
                return {
                    **detail,
                    "idempotent_replay": True,
                }

            now = _utc_now()
            rec.acknowledged = True
            rec.acknowledged_by = final_actor
            rec.acknowledged_at = now
            rec.audit_logs.append(
                {
                    "action": "alert_acknowledged",
                    "actor": final_actor,
                    "role": role,
                    "timestamp": now.isoformat(),
                    "detail": {
                        "alert_status_preserved": matched["status"],
                        "note": note,
                    },
                }
            )

            detail = self._get_alert_detail_locked(alert_id)
            return {
                **detail,
                "idempotent_replay": False,
            }