

import logging
import os
import signal
import threading
import time

from src.create_app import create_app


logger = logging.getLogger("ar_imms.alert_worker")


def configure_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_poll_interval() -> int:
    raw_value = os.getenv(
        "TELEMETRY_POLL_INTERVAL_SECONDS",
        "5",
    )

    try:
        interval = int(raw_value)
    except ValueError as error:
        raise RuntimeError(
            "TELEMETRY_POLL_INTERVAL_SECONDS phải là số nguyên."
        ) from error

    if interval <= 0:
        raise RuntimeError(
            "TELEMETRY_POLL_INTERVAL_SECONDS phải lớn hơn 0."
        )

    return interval


def run_worker(stop_event: threading.Event) -> None:
    app = create_app()
    database = app.extensions["database"]
    container = app.extensions["container"]

    poll_interval = get_poll_interval()

    logger.info(
        "Alert Worker started. Poll interval: %s seconds.",
        poll_interval,
    )

    try:
        while not stop_event.is_set():
            cycle_started = time.monotonic()

            try:
                with app.app_context():
                    result = container.alert_detector.run_cycle()

                logger.info(
                    "Alert detection cycle completed: %s",
                    result,
                )

            except Exception:
                logger.exception(
                    "Alert detection cycle failed. "
                    "Worker will retry in the next cycle."
                )

            elapsed = time.monotonic() - cycle_started
            wait_seconds = max(0, poll_interval - elapsed)

            if stop_event.wait(wait_seconds):
                break

    finally:
        logger.info("Closing database connections.")
        database.dispose()
        logger.info("Alert Worker stopped.")


def main() -> None:
    configure_logging()

    stop_event = threading.Event()

    def handle_shutdown(signum, frame) -> None:
        logger.info(
            "Received shutdown signal %s.",
            signum,
        )
        stop_event.set()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    run_worker(stop_event)


if __name__ == "__main__":
    main()
