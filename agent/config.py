import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "https://localhost:5002",
).rstrip("/")

TELEMETRY_ENDPOINT = os.getenv(
    "TELEMETRY_ENDPOINT",
    "/telemetry",
)

NODE_ID = os.getenv("NODE_ID", "").strip()

# Mutual TLS certificate configuration
CLIENT_CERT_PATH = Path(
    os.getenv(
        "CLIENT_CERT_PATH",
        str(BASE_DIR / "certs-v2" / "agent.crt"),
    )
)

CLIENT_KEY_PATH = Path(
    os.getenv(
        "CLIENT_KEY_PATH",
        str(BASE_DIR / "certs-v2" / "agent.key"),
    )
)

CA_CERT_PATH = Path(
    os.getenv(
        "CA_CERT_PATH",
        str(BASE_DIR / "certs-v2" / "ca.crt"),
    )
)

SEND_INTERVAL_SECONDS = float(
    os.getenv("SEND_INTERVAL_SECONDS", "5")
)

REQUEST_TIMEOUT_SECONDS = float(
    os.getenv("REQUEST_TIMEOUT_SECONDS", "5")
)

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

RETRY_DELAY_SECONDS = float(
    os.getenv("RETRY_DELAY_SECONDS", "2")
)
