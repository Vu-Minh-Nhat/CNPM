import os
from flask import Flask
from flask_cors import CORS

from src.api.controllers.alert_rules_controller import register_alert_rule_routes
from src.services.alert_detector_service import AlertDetectorService, AlertRuleManager
from src.worker.alert_poller import AlertPoller, should_start_poller_in_flask


def attach_alerting_system(app: Flask) -> None:
    if app.extensions.get("alerting_attached"):
        return

    rule_manager = AlertRuleManager()
    detector = AlertDetectorService(rule_manager)
    poll_interval = float(os.environ.get("ALERT_POLLER_INTERVAL_SECONDS", "10.0"))
    poller = AlertPoller(detector=detector, interval_seconds=poll_interval)

    app.extensions["alert_rule_manager"] = rule_manager
    app.extensions["alert_detector"] = detector
    app.extensions["alert_poller"] = poller
    app.extensions["alerting_attached"] = True

    register_alert_rule_routes(app, rule_manager, detector=detector)

    if should_start_poller_in_flask(app.debug):
        poller.start()


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, origins=os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(","))

    # Giữ nguyên các blueprint / service khởi tạo gốc của dự án tại đây
    attach_alerting_system(app)
    return app