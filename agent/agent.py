import logging
import platform
import time
import uuid
from datetime import datetime, timezone

import psutil
import requests

from config import (
    AUTH_TOKEN,
    BACKEND_URL,
    MAX_RETRIES,
    NODE_ID,
    REQUEST_TIMEOUT_SECONDS,
    RETRY_DELAY_SECONDS,
    SEND_INTERVAL_SECONDS,
    TELEMETRY_ENDPOINT,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("collector-agent")


def collect_metrics() -> dict:
    """Collect CPU, RAM and disk usage."""
    disk_path = "C:\\" if platform.system() == "Windows" else "/"

    return {
        "cpu_percent": round(
            psutil.cpu_percent(interval=1),
            2,
        ),
        "memory_percent": round(
            psutil.virtual_memory().percent,
            2,
        ),
        "disk_percent": round(
            psutil.disk_usage(disk_path).percent,
            2,
        ),
    }


def send_telemetry(payload: dict) -> bool:
    """Send telemetry to Backend with limited retries."""
    url = f"{BACKEND_URL}{TELEMETRY_ENDPOINT}"

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json",
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            if 200 <= response.status_code < 300:
                logger.info(
                    "Telemetry sent successfully: message_id=%s",
                    payload["message_id"],
                )
                return True

            # Do not retry invalid/authentication/permission errors.
            if response.status_code in (400, 401, 403, 404, 409):
                logger.error(
                    "Telemetry rejected: status=%s",
                    response.status_code,
                )
                return False

            logger.warning(
                "Telemetry request failed: status=%s, attempt=%s/%s",
                response.status_code,
                attempt,
                MAX_RETRIES,
            )

        except requests.RequestException as error:
            logger.warning(
                "Connection failed: attempt=%s/%s (%s)",
                attempt,
                MAX_RETRIES,
                error.__class__.__name__,
            )

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_SECONDS)

    logger.error(
        "Telemetry delivery failed after %s attempts: message_id=%s",
        MAX_RETRIES,
        payload["message_id"],
    )

    return False


def build_payload() -> dict:
    """Create one telemetry message."""
    metrics = collect_metrics()

    return {
        "message_id": str(uuid.uuid4()),
        "node_id": NODE_ID,
        "measured_at": datetime.now(timezone.utc).isoformat(),
        **metrics,
    }


def validate_config() -> None:
    """Validate required configuration."""
    if not NODE_ID:
        raise RuntimeError("NODE_ID chưa được cấu hình.")

    if not AUTH_TOKEN:
        raise RuntimeError("AUTH_TOKEN chưa được cấu hình.")


def main() -> None:
    validate_config()

    logger.info("Collector Agent started.")

    logger.info(
        "Backend=%s%s | interval=%ss",
        BACKEND_URL,
        TELEMETRY_ENDPOINT,
        SEND_INTERVAL_SECONDS,
    )

    while True:
        try:
            payload = build_payload()

            logger.info(
                "Collected telemetry: CPU=%.2f%%, RAM=%.2f%%, Disk=%.2f%%",
                payload["cpu_percent"],
                payload["memory_percent"],
                payload["disk_percent"],
            )

            send_telemetry(payload)

        except Exception as error:
            logger.exception(
                "Unexpected agent error: %s",
                error.__class__.__name__,
            )

        time.sleep(SEND_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()