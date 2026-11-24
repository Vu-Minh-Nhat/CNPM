from datetime import datetime, timezone
from typing import Any, Dict, Optional

from flask import Blueprint, current_app, jsonify, request

from src.services.alert_detector_service import AlertDetectorService, TelemetrySample

telemetry_bp = Blueprint("telemetry", __name__, url_prefix="/telemetry")


def _parse_timestamp_utc(ts_raw: Any) -> datetime:
    if isinstance(ts_raw, datetime):
        return ts_raw if ts_raw.tzinfo is not None else ts_raw.replace(tzinfo=timezone.utc)
    if isinstance(ts_raw, str) and ts_raw.strip():
        parsed = datetime.fromisoformat(ts_raw.strip().replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def _extract_metrics(payload: Dict[str, Any]) -> Dict[str, Optional[float]]:
    metrics: Dict[str, Optional[float]] = {}
    raw_metrics = payload.get("metrics")
    if isinstance(raw_metrics, dict):
        for key in ("cpu", "ram", "disk"):
            if key in raw_metrics:
                val = raw_metrics[key]
                metrics[key] = None if val is None else float(val)

    fallback_map = {
        "cpu": ("cpu", "cpu_percent"),
        "ram": ("ram", "memory_percent", "ram_percent"),
        "disk": ("disk", "disk_percent"),
    }
    for target_key, aliases in fallback_map.items():
        if target_key in metrics:
            continue
        for alias in aliases:
            if alias in payload:
                val = payload[alias]
                metrics[target_key] = None if val is None else float(val)
                break

    return metrics


def forward_telemetry_to_detector(
    payload: Dict[str, Any],
    detector: Optional[AlertDetectorService] = None,
) -> None:
    target_detector = detector or current_app.extensions.get("alert_detector")
    if target_detector is None or not isinstance(payload, dict):
        return

    node_id = payload.get("node_id")
    if not node_id:
        return

    metrics = _extract_metrics(payload)
    ts = _parse_timestamp_utc(payload.get("timestamp"))
    message_id = payload.get("message_id")

    sample = TelemetrySample(
        node_id=str(node_id),
        timestamp=ts,
        metrics=metrics,
        message_id=str(message_id) if message_id is not None else None,
    )
    target_detector.ingest_telemetry(sample)


@telemetry_bp.post("")
def ingest_telemetry():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict) or not payload.get("node_id"):
        return jsonify({"error": "Missing 'node_id'"}), 400

    forward_telemetry_to_detector(payload)
    return jsonify({"status": "accepted", "node_id": str(payload["node_id"])}), 202