import os

from dotenv import load_dotenv

load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:5000",
).rstrip("/")

TELEMETRY_ENDPOINT = os.getenv(
    "TELEMETRY_ENDPOINT",
    "/telemetry",
)

NODE_ID = os.getenv("NODE_ID", "").strip()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

JWT_SECRET = os.getenv("JWT_SECRET", "").strip()

AUTH_TOKEN = os.getenv("AUTH_TOKEN", "").strip()

SEND_INTERVAL_SECONDS = float(
    os.getenv("SEND_INTERVAL_SECONDS", "5")
)

REQUEST_TIMEOUT_SECONDS = float(
    os.getenv("REQUEST_TIMEOUT_SECONDS", "5")
)

MAX_RETRIES = int(
    os.getenv("MAX_RETRIES", "3")
)

RETRY_DELAY_SECONDS = float(
    os.getenv("RETRY_DELAY_SECONDS", "2")
)
