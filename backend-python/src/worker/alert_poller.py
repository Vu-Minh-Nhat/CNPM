import os
import threading
import time
from typing import Optional
from src.services.alert_detector_service import AlertDetectorService


class AlertPoller:
    def __init__(self, detector: AlertDetectorService, interval_seconds: float = 10.0) -> None:
        self.detector = detector
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="alert-poller", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            self.detector.check_node_connectivity()
            self._stop_event.wait(self.interval_seconds)


def should_start_poller_in_flask(app_debug: bool) -> bool:
    """Tránh tạo 2 poller khi chạy Flask với debug=True / reloader."""
    if not app_debug:
        return True
    return os.environ.get("WERKZEUG_RUN_MAIN") == "true"


def run_standalone_poller(detector: AlertDetectorService, interval_seconds: float = 10.0) -> None:
    poller = AlertPoller(detector=detector, interval_seconds=interval_seconds)
    poller.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        poller.stop()