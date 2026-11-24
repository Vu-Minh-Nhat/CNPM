
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

from flask import Flask

from src.api.controllers.telemetry_queries_controller import (
    create_telemetry_queries_blueprint,
)
from src.api.error_handlers import register_error_handlers
from src.domain.constants import Role
from src.domain.exceptions import AuthenticationError
from src.services.telemetry_query_service import TelemetryQueryService


class FakeServerRepository:
    def __init__(self):
        self.node_ids = set()

    def find_by_id(self, node_id):
        if node_id in self.node_ids:
            return SimpleNamespace(id=node_id)

        return None


class FakeTelemetryRepository:
    def __init__(self):
        self.records = []

    def get_latest(self, node_id):
        records = [
            record
            for record in self.records
            if record.node_id == node_id
        ]

        if not records:
            return None

        return max(
            records,
            key=lambda record: (
                record.measured_at,
                record.received_at,
                record.id,
            ),
        )

    def get_last_received_at(self, node_id):
        records = [
            record.received_at
            for record in self.records
            if record.node_id == node_id
        ]

        return max(records) if records else None

    def list_history(self, node_id, *, start, end, limit):
        records = [
            record
            for record in self.records
            if (
                record.node_id == node_id
                and start <= record.measured_at < end
            )
        ]

        records.sort(
            key=lambda record: (
                record.measured_at,
                record.received_at,
                record.id,
            )
        )

        return records[:limit]


class FakeSessionService:
    def authenticate_token(self, token):
        if token == "invalid-token":
            raise AuthenticationError("Token không hợp lệ.")

        roles = {
            "admin-token": Role.ADMINISTRATOR,
            "operator-token": Role.OPERATOR,
            "technician-token": Role.TECHNICIAN,
            "guest-token": "Guest",
        }

        role = roles.get(token)

        if role is None:
            raise AuthenticationError("Token không hợp lệ.")

        return SimpleNamespace(
            id=str(uuid4()),
            role=role,
        )


class TestTelemetryQueriesAPI(unittest.TestCase):
    def setUp(self):
        self.node_id = str(uuid4())

        self.now = datetime(
            2026, 11, 24, 8, 0, 0,
            tzinfo=timezone.utc,
        )

        self.server_repository = FakeServerRepository()
        self.server_repository.node_ids.add(self.node_id)

        self.telemetry_repository = FakeTelemetryRepository()

        self.query_service = TelemetryQueryService(
            telemetry_repository=self.telemetry_repository,
            server_repository=self.server_repository,
            stale_after_seconds=30,
            offline_after_seconds=90,
            poll_interval_seconds=5,
            clock=lambda: self.now,
        )

        self.session_service = FakeSessionService()

        self.app = Flask(__name__)

        register_error_handlers(self.app)

        self.app.register_blueprint(
            create_telemetry_queries_blueprint(
                query_service=self.query_service,
                session_service=self.session_service,
            )
        )

        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        self._create_sample_records()

    def _create_record(
        self,
        measured_at,
        received_at,
        cpu=50.0,
        memory=60.0,
        disk=70.0,
    ):
        record = SimpleNamespace(
            id=str(uuid4()),
            message_id=str(uuid4()),
            node_id=self.node_id,
            measured_at=measured_at,
            received_at=received_at,
            cpu_percent=cpu,
            memory_percent=memory,
            disk_percent=disk,
        )

        self.telemetry_repository.records.append(record)

        return record

    def _create_sample_records(self):
        # Bản ghi thứ nhất được nhận muộn hơn,
        # nhưng có measured_at cũ hơn.
        self._create_record(
            measured_at=self.now - timedelta(minutes=10),
            received_at=self.now - timedelta(minutes=1),
            cpu=20.0,
        )

        self._create_record(
            measured_at=self.now - timedelta(minutes=5),
            received_at=self.now - timedelta(minutes=4),
            cpu=80.0,
        )

        self._create_record(
            measured_at=self.now - timedelta(minutes=2),
            received_at=self.now - timedelta(minutes=2),
            cpu=90.0,
        )

    def _headers(self, token="admin-token"):
        return {
            "Authorization": f"Bearer {token}",
        }

    def _latest_url(self, node_id=None):
        target = node_id or self.node_id

        return f"/telemetry/nodes/{target}/latest"

    def _history_url(self, node_id=None, **params):
        target = node_id or self.node_id

        from urllib.parse import urlencode

        query = urlencode(params)

        return f"/telemetry/nodes/{target}/history?{query}"

    # --------------------------------------------------------------
    # Latest API
    # --------------------------------------------------------------

    def test_01_latest_returns_latest_by_measured_at(self):
        response = self.client.get(
            self._latest_url(),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        self.assertEqual(body["node_id"], self.node_id)
        self.assertIsNotNone(body["latest"])

        # Latest phải dựa trên measured_at,
        # không phải received_at.
        self.assertEqual(
            body["latest"]["cpu_percent"],
            90.0,
        )

        self.assertEqual(
            body["latest"]["measured_at"],
            (
                self.now - timedelta(minutes=2)
            ).isoformat(),
        )

        self.assertEqual(
            body["latest"]["node_id"],
            self.node_id,
        )

        self.assertIn("received_at", body["latest"])
        self.assertIn("monitoring", body)
        self.assertIn("poll_interval_seconds", body)

    def test_02_latest_without_telemetry_returns_null(self):
        self.telemetry_repository.records.clear()

        response = self.client.get(
            self._latest_url(),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        self.assertIsNone(body["latest"])
        self.assertEqual(body["monitoring"]["data_status"], "no_data")
        self.assertEqual(
            body["monitoring"]["connection_status"],
            "never_seen",
        )

    # --------------------------------------------------------------
    # History API
    # --------------------------------------------------------------

    def test_03_history_returns_records_in_requested_range(self):
        start = (
            self.now - timedelta(minutes=6)
        ).isoformat()

        end = (
            self.now - timedelta(minutes=1)
        ).isoformat()

        response = self.client.get(
            self._history_url(
                start=start,
                end=end,
                limit=100,
            ),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        self.assertEqual(body["node_id"], self.node_id)
        self.assertEqual(body["count"], 2)

        self.assertEqual(
            body["items"][0]["cpu_percent"],
            80.0,
        )

        self.assertEqual(
            body["items"][1]["cpu_percent"],
            90.0,
        )

        for item in body["items"]:
            measured_at = datetime.fromisoformat(
                item["measured_at"]
            )

            self.assertGreaterEqual(
                measured_at,
                datetime.fromisoformat(start),
            )

            self.assertLess(
                measured_at,
                datetime.fromisoformat(end),
            )

    def test_04_history_end_is_exclusive(self):
        start = (
            self.now - timedelta(minutes=5)
        ).isoformat()

        end = (
            self.now - timedelta(minutes=2)
        ).isoformat()

        response = self.client.get(
            self._history_url(
                start=start,
                end=end,
            ),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        # Bản ghi đúng tại end không được trả về.
        self.assertEqual(body["count"], 1)
        self.assertEqual(
            body["items"][0]["cpu_percent"],
            80.0,
        )

    def test_05_history_empty_result(self):
        start = (
            self.now - timedelta(days=2)
        ).isoformat()

        end = (
            self.now - timedelta(days=1)
        ).isoformat()

        response = self.client.get(
            self._history_url(
                start=start,
                end=end,
            ),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        self.assertEqual(body["count"], 0)
        self.assertEqual(body["items"], [])

    def test_06_history_respects_limit(self):
        start = (
            self.now - timedelta(minutes=20)
        ).isoformat()

        end = self.now.isoformat()

        response = self.client.get(
            self._history_url(
                start=start,
                end=end,
                limit=1,
            ),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        self.assertEqual(body["count"], 1)
        self.assertEqual(body["limit"], 1)
        self.assertTrue(body["limit_reached"])

    # --------------------------------------------------------------
    # Node ID validation
    # --------------------------------------------------------------

    def test_07_invalid_node_uuid_returns_400(self):
        response = self.client.get(
            self._latest_url("invalid-uuid"),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)

    def test_08_missing_node_returns_404(self):
        unknown_node_id = str(uuid4())

        response = self.client.get(
            self._latest_url(unknown_node_id),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 404)

    # --------------------------------------------------------------
    # Timestamp validation
    # --------------------------------------------------------------

    def test_09_history_missing_start_returns_400(self):
        response = self.client.get(
            self._history_url(
                end=self.now.isoformat(),
            ),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)

    def test_10_history_missing_end_returns_400(self):
        response = self.client.get(
            self._history_url(
                start=self.now.isoformat(),
            ),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)

    def test_11_history_invalid_timestamp_returns_400(self):
        response = self.client.get(
            self._history_url(
                start="not-a-timestamp",
                end=self.now.isoformat(),
            ),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)

    def test_12_history_timestamp_without_timezone_returns_400(self):
        response = self.client.get(
            self._history_url(
                start="2026-11-24T08:00:00",
                end="2026-11-24T09:00:00",
            ),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)

    def test_13_history_start_must_be_before_end(self):
        timestamp = self.now.isoformat()

        response = self.client.get(
            self._history_url(
                start=timestamp,
                end=timestamp,
            ),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------------------
    # Limit validation
    # --------------------------------------------------------------

    def test_14_history_invalid_limit_returns_400(self):
        for limit in ("abc", "1.5", "0", "-1", "1001"):
            with self.subTest(limit=limit):
                response = self.client.get(
                    self._history_url(
                        start=(
                            self.now - timedelta(hours=1)
                        ).isoformat(),
                        end=self.now.isoformat(),
                        limit=limit,
                    ),
                    headers=self._headers(),
                )

                self.assertEqual(response.status_code, 400)

    def test_15_history_default_limit_is_1000(self):
        response = self.client.get(
            self._history_url(
                start=(
                    self.now - timedelta(hours=1)
                ).isoformat(),
                end=self.now.isoformat(),
            ),
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["limit"], 1000)

    # --------------------------------------------------------------
    # Authentication and authorization
    # --------------------------------------------------------------

    def test_16_missing_authorization_returns_401(self):
        response = self.client.get(
            self._latest_url(),
        )

        self.assertEqual(response.status_code, 401)

    def test_17_invalid_token_returns_401(self):
        response = self.client.get(
            self._latest_url(),
            headers=self._headers("invalid-token"),
        )

        self.assertEqual(response.status_code, 401)

    def test_18_all_defined_roles_can_read_telemetry(self):
        tokens = (
            "admin-token",
            "operator-token",
            "technician-token",
        )

        for token in tokens:
            with self.subTest(token=token):
                response = self.client.get(
                    self._latest_url(),
                    headers=self._headers(token),
                )

                self.assertEqual(response.status_code, 200)

    def test_19_undefined_role_returns_403(self):
        response = self.client.get(
            self._latest_url(),
            headers=self._headers("guest-token"),
        )

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main(verbosity=2)
