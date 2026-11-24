
import os
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from flask import Flask

from src.api.controllers.telemetry_controller import (
    create_telemetry_blueprint,
)
from src.domain.exceptions import ResourceConflictError


class TestTelemetryAPI(unittest.TestCase):
    def setUp(self):
        self.agent_key = "test-agent-key"
        self.node_id = str(uuid4())

        self.env = patch.dict(os.environ, {
            "TELEMETRY_AGENT_KEY": self.agent_key,
            "TELEMETRY_AGENT_NODE_IDS": self.node_id,
        })
        self.env.start()
        self.addCleanup(self.env.stop)

        self.telemetry_service = MagicMock()
        self.session_service = MagicMock()

        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_telemetry_blueprint(
                telemetry_service=self.telemetry_service,
                session_service=self.session_service,
            )
        )
        self.app.config["TESTING"] = True
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

    def _headers(self, key=None):
        return {
            "X-Agent-Key": self.agent_key if key is None else key
        }

    def test_01_missing_agent_key(self):
        response = self.client.post(
            "/telemetry",
            json=self.payload,
        )

        self.assertEqual(response.status_code, 401)
        self.telemetry_service.ingest.assert_not_called()

    def test_02_invalid_agent_key(self):
        response = self.client.post(
            "/telemetry",
            json=self.payload,
            headers=self._headers("wrong-key"),
        )

        self.assertEqual(response.status_code, 401)
        self.telemetry_service.ingest.assert_not_called()

    def test_03_agent_cannot_send_to_unassigned_node(self):
        payload = {
            **self.payload,
            "node_id": str(uuid4()),
        }

        response = self.client.post(
            "/telemetry",
            json=payload,
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 403)
        self.telemetry_service.ingest.assert_not_called()

    def test_04_missing_required_field(self):
        payload = dict(self.payload)
        del payload["cpu_percent"]

        response = self.client.post(
            "/telemetry",
            json=payload,
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)
        self.telemetry_service.ingest.assert_not_called()

    def test_05_invalid_metric_value(self):
        payload = {
            **self.payload,
            "cpu_percent": 150,
        }

        response = self.client.post(
            "/telemetry",
            json=payload,
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)
        self.telemetry_service.ingest.assert_not_called()

    def test_06_valid_telemetry(self):
        response = self.client.post(
            "/telemetry",
            json=self.payload,
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["message_id"],
            self.payload["message_id"],
        )
        self.assertEqual(
            response.get_json()["node_id"],
            self.node_id,
        )
        self.telemetry_service.ingest.assert_called_once()

    def test_07_conflicting_message_id_returns_409(self):
        self.telemetry_service.ingest.side_effect = (
            ResourceConflictError(
                "message_id đã tồn tại với payload khác."
            )
        )

        response = self.client.post(
            "/telemetry",
            json=self.payload,
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":
    unittest.main(verbosity=2)
