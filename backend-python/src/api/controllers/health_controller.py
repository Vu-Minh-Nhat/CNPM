from datetime import datetime, timezone
from time import monotonic

from flask import Blueprint

health_bp = Blueprint("health", __name__)

_started_at = monotonic()


@health_bp.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ar-imms-backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptimeSeconds": int(monotonic() - _started_at),
    }, 200