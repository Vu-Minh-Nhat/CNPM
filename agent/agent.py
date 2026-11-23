import logging
import platform
import time
import uuid
from datetime import datetime, timezone

import psutil
import requests

from config import (
    BACKEND_URL,
    CA_CERT_PATH,
    CLIENT_CERT_PATH,
    CLIENT_KEY_PATH,
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
    """Send telemetry to Backend using mutual TLS."""

    url = f"{BACKEND_URL}{TELEMETRY_ENDPOINT}"

    headers = {
        "Content-Type": "application/json",
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                cert=(
                    str(CLIENT_CERT_PATH),
                    str(CLIENT_KEY_PATH),
                ),
                verify=str(CA_CERT_PATH),
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
    """Validate required configuration and TLS certificates."""

    if not NODE_ID:
        raise RuntimeError("NODE_ID chua duoc cau hinh.")

    if not BACKEND_URL.startswith("https://"):
        raise RuntimeError(
            "BACKEND_URL phai su dung HTTPS."
        )

    required_files = {
        "Client certificate": CLIENT_CERT_PATH,
        "Client private key": CLIENT_KEY_PATH,
        "CA certificate": CA_CERT_PATH,
    }

    for name, path in required_files.items():
        if not path.is_file():
            raise RuntimeError(
                f"{name} khong ton tai: {path}"
            )

    if MAX_RETRIES < 1:
        raise RuntimeError("MAX_RETRIES phai lon hon hoac bang 1.")

    if SEND_INTERVAL_SECONDS <= 0:
        raise RuntimeError(
            "SEND_INTERVAL_SECONDS phai lon hon 0."
        )

    if REQUEST_TIMEOUT_SECONDS <= 0:
        raise RuntimeError(
            "REQUEST_TIMEOUT_SECONDS phai lon hon 0."
        )

    if RETRY_DELAY_SECONDS < 0:
        raise RuntimeError(
            "RETRY_DELAY_SECONDS khong duoc am."
        )


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
