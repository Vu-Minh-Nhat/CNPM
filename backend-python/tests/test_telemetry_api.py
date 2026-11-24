
import hashlib
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from flask import Flask

from src.api.controllers.telemetry_controller import (
    create_telemetry_blueprint,
)
from src.domain.exceptions import ResourceConflictError


class FakeTLSSocket:
    """Giả lập TLS socket có client certificate."""

    def __init__(self, certificate_der):
        self.certificate_der = certificate_der

    def getpeercert(self, binary_form=False):
        if binary_form:
            return self.certificate_der
        return {}


class TestTelemetryAPI(unittest.TestCase):

    def setUp(self):
        self.node_id = str(uuid4())
        self.agent_id = str(uuid4())

        self.certificate_der = b"fake-client-certificate"
        self.fingerprint = hashlib.sha256(
            self.certificate_der
        ).hexdigest()

        self.agent = SimpleNamespace(
            id=self.agent_id,
            is_active=True,
        )

        self.telemetry_service = MagicMock()
        self.session_service = MagicMock()
        self.agent_service = MagicMock()

        self.agent_service.authenticate_agent.return_value = self.agent
        self.agent_service.has_node_access.return_value = True

        self.app = Flask(__name__)
        self.app.config["TESTING"] = True

        self.app.register_blueprint(
            create_telemetry_blueprint(
                telemetry_service=self.telemetry_service,
                session_service=self.session_service,
                agent_service=self.agent_service,
            )
        )

        self.client = self.app.test_client()

        self.payload = {
            "message_id": str(uuid4()),
            "node_id": self.node_id,
            "measured_at": "2026-11-16T10:00:00+07:00",
            "cpu_percent": 35.5,
            "memory_percent": 60.0,
            "disk_percent": 45.2,
        }

        now = datetime.now(timezone.utc)

        self.telemetry_service.ingest.return_value = SimpleNamespace(
            id=str(uuid4()),
            message_id=self.payload["message_id"],
            node_id=self.node_id,
            measured_at=now,
            cpu_percent=35.5,
            memory_percent=60.0,
            disk_percent=45.2,
            received_at=now,
        )

        self.tls_socket = FakeTLSSocket(self.certificate_der)

    def _post_with_certificate(self, payload=None):
        return self.client.post(
            "/telemetry",
            json=self.payload if payload is None else payload,
            environ_overrides={
                "werkzeug.socket": self.tls_socket,
            },
        )

    # ---------------------------------------------------------
    # 1. TLS authentication
    # ---------------------------------------------------------

    def test_01_missing_tls_certificate(self):
        response = self.client.post(
            "/telemetry",
            json=self.payload,
        )

        self.assertEqual(response.status_code, 401)
        self.agent_service.authenticate_agent.assert_not_called()
        self.telemetry_service.ingest.assert_not_called()

    def test_02_unknown_agent_certificate(self):
        self.agent_service.authenticate_agent.return_value = None

        response = self._post_with_certificate()

        self.assertEqual(response.status_code, 401)

        self.agent_service.authenticate_agent.assert_called_once_with(
            self.fingerprint
        )
        self.telemetry_service.ingest.assert_not_called()

    # ---------------------------------------------------------
    # 2. Node access authorization
    # ---------------------------------------------------------

    def test_03_agent_cannot_send_to_unassigned_node(self):
        self.agent_service.has_node_access.return_value = False

        response = self._post_with_certificate()

        self.assertEqual(response.status_code, 403)

        self.agent_service.has_node_access.assert_called_once_with(
            self.agent_id,
            self.node_id,
        )
        self.telemetry_service.ingest.assert_not_called()

    # ---------------------------------------------------------
    # 3. Payload validation
    # ---------------------------------------------------------

    def test_04_missing_required_field(self):
        payload = dict(self.payload)
        del payload["cpu_percent"]

        response = self._post_with_certificate(payload)

        self.assertEqual(response.status_code, 400)
        self.telemetry_service.ingest.assert_not_called()

    def test_05_invalid_metric_value(self):
        payload = {
            **self.payload,
            "cpu_percent": 150,
        }

        response = self._post_with_certificate(payload)

        self.assertEqual(response.status_code, 400)
        self.telemetry_service.ingest.assert_not_called()

    # ---------------------------------------------------------
    # 4. Successful ingestion
    # ---------------------------------------------------------

    def test_06_valid_telemetry(self):
        response = self._post_with_certificate()

        self.assertEqual(response.status_code, 200)

        response_data = response.get_json()

        self.assertEqual(
            response_data["message_id"],
            self.payload["message_id"],
        )
        self.assertEqual(
            response_data["node_id"],
            self.node_id,
        )

        self.agent_service.authenticate_agent.assert_called_once_with(
            self.fingerprint
        )
        self.agent_service.has_node_access.assert_called_once_with(
            self.agent_id,
            self.node_id,
        )
        self.telemetry_service.ingest.assert_called_once()

    # ---------------------------------------------------------
    # 5. Duplicate/conflicting message
    # ---------------------------------------------------------

    def test_07_conflicting_message_id_returns_409(self):
        self.telemetry_service.ingest.side_effect = (
            ResourceConflictError(
                "message_id đã tồn tại với payload khác."
            )
        )

        response = self._post_with_certificate()

        self.assertEqual(response.status_code, 409)
        self.telemetry_service.ingest.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
