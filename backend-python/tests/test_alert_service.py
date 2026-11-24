
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from src.domain.exceptions import (
    ResourceNotFoundError,
    ValidationError,
)
from src.domain.models.alert import Alert
from src.services.alert_service import AlertService


class TestAlertService(unittest.TestCase):

    def setUp(self):
        self.repository = MagicMock()
        self.service = AlertService(self.repository)

        self.now = datetime(
            2026, 11, 24, 10, 0, 0,
            tzinfo=timezone.utc,
        )

        self.alert_id = str(uuid4())
        self.node_id = str(uuid4())
        self.rule_id = str(uuid4())
        self.actor_id = str(uuid4())

    def make_alert(
        self,
        status="FIRING",
        acknowledged_by=None,
        acknowledged_at=None,
        recovered_at=None,
    ):
        return Alert(
            id=self.alert_id,
            node_id=self.node_id,
            rule_id=self.rule_id,
            metric="cpu_percent",
            operator=">=",
            threshold=80.0,
            severity="HIGH",
            status=status,
            message="CPU usage exceeded threshold",
            triggered_at=self.now - timedelta(minutes=5),
            acknowledged_at=acknowledged_at,
            recovered_at=recovered_at,
            triggered_value=95.5,
            acknowledged_by=acknowledged_by,
        )

    # -----------------------------------------------------
    # Alert detail
    # -----------------------------------------------------

    def test_01_get_alert_returns_complete_information(self):
        alert = self.make_alert()
        self.repository.find_by_id.return_value = alert

        result = self.service.get_alert(self.alert_id)

        self.repository.find_by_id.assert_called_once_with(
            self.alert_id
        )

        self.assertEqual(result["id"], self.alert_id)
        self.assertEqual(result["node_id"], self.node_id)
        self.assertEqual(result["rule_id"], self.rule_id)
        self.assertEqual(result["metric"], "cpu_percent")
        self.assertEqual(result["threshold"], 80.0)
        self.assertEqual(result["triggered_value"], 95.5)
        self.assertEqual(result["severity"], "HIGH")
        self.assertEqual(result["status"], "FIRING")
        self.assertIsNone(result["acknowledged_by"])
        self.assertIsNone(result["acknowledged_at"])
        self.assertIsNone(result["recovered_at"])

    def test_02_get_missing_alert_raises_not_found(self):
        self.repository.find_by_id.return_value = None

        with self.assertRaises(ResourceNotFoundError):
            self.service.get_alert(self.alert_id)

    # -----------------------------------------------------
    # Alert listing and pagination
    # -----------------------------------------------------

    def test_03_list_alerts_returns_items_and_pagination(self):
        alerts = [
            self.make_alert(),
            self.make_alert(),
        ]

        self.repository.query_alerts.return_value = (
            alerts,
            45,
        )

        result = self.service.list_alerts(
            page=2,
            page_size=20,
        )

        self.repository.query_alerts.assert_called_once_with(
            node_id=None,
            metric=None,
            severity=None,
            status=None,
            start_time=None,
            end_time=None,
            page=2,
            page_size=20,
        )

        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(
            result["pagination"],
            {
                "page": 2,
                "page_size": 20,
                "total": 45,
                "total_pages": 3,
            },
        )

    def test_04_list_alerts_forwards_all_filters(self):
        start_time = self.now - timedelta(days=1)
        end_time = self.now

        self.repository.query_alerts.return_value = ([], 0)

        self.service.list_alerts(
            node_id=self.node_id,
            metric="cpu_percent",
            severity="HIGH",
            status="FIRING",
            start_time=start_time,
            end_time=end_time,
            page=1,
            page_size=10,
        )

        self.repository.query_alerts.assert_called_once_with(
            node_id=self.node_id,
            metric="cpu_percent",
            severity="HIGH",
            status="FIRING",
            start_time=start_time,
            end_time=end_time,
            page=1,
            page_size=10,
        )

    def test_05_empty_list_has_zero_total_pages(self):
        self.repository.query_alerts.return_value = ([], 0)

        result = self.service.list_alerts()

        self.assertEqual(result["items"], [])
        self.assertEqual(
            result["pagination"]["total"],
            0,
        )
        self.assertEqual(
            result["pagination"]["total_pages"],
            0,
        )

    # -----------------------------------------------------
    # Pagination validation
    # -----------------------------------------------------

    def test_06_invalid_page_values_are_rejected(self):
        invalid_values = [
            0,
            -1,
            True,
            1.5,
            "1",
            None,
        ]

        for value in invalid_values:
            with self.subTest(page=value):
                with self.assertRaises(ValidationError):
                    self.service.list_alerts(page=value)

        self.repository.query_alerts.assert_not_called()

    def test_07_invalid_page_size_values_are_rejected(self):
        invalid_values = [
            0,
            -1,
            101,
            True,
            1.5,
            "20",
            None,
        ]

        for value in invalid_values:
            with self.subTest(page_size=value):
                with self.assertRaises(ValidationError):
                    self.service.list_alerts(
                        page_size=value
                    )

        self.repository.query_alerts.assert_not_called()

    def test_08_page_size_boundaries_are_accepted(self):
        for page_size in (1, 100):
            with self.subTest(page_size=page_size):
                self.repository.reset_mock()
                self.repository.query_alerts.return_value = (
                    [],
                    0,
                )

                result = self.service.list_alerts(
                    page_size=page_size
                )

                self.assertEqual(
                    result["pagination"]["page_size"],
                    page_size,
                )

    # -----------------------------------------------------
    # Acknowledgement
    # -----------------------------------------------------

    def test_09_acknowledge_alert_forwards_actor_and_time(self):
        acknowledged = self.make_alert(
            status="ACKNOWLEDGED",
            acknowledged_by=self.actor_id,
            acknowledged_at=self.now,
        )

        self.repository.acknowledge.return_value = acknowledged

        result = self.service.acknowledge_alert(
            alert_id=self.alert_id,
            actor_id=self.actor_id,
        )

        self.repository.acknowledge.assert_called_once()

        call = self.repository.acknowledge.call_args.kwargs

        self.assertEqual(call["alert_id"], self.alert_id)
        self.assertEqual(call["actor_id"], self.actor_id)
        self.assertIsNotNone(call["acknowledged_at"])
        self.assertIsNotNone(call["acknowledged_at"].tzinfo)

        self.assertEqual(result["status"], "ACKNOWLEDGED")
        self.assertEqual(
            result["acknowledged_by"],
            self.actor_id,
        )
        self.assertIsNotNone(result["acknowledged_at"])
        self.assertIsNone(result["recovered_at"])

    def test_10_acknowledge_missing_alert_raises_not_found(self):
        self.repository.acknowledge.return_value = None

        with self.assertRaises(ResourceNotFoundError):
            self.service.acknowledge_alert(
                alert_id=self.alert_id,
                actor_id=self.actor_id,
            )

    def test_11_acknowledge_rejects_empty_actor_id(self):
        invalid_actor_ids = [
            "",
            " ",
            None,
            123,
        ]

        for actor_id in invalid_actor_ids:
            with self.subTest(actor_id=actor_id):
                with self.assertRaises(ValidationError):
                    self.service.acknowledge_alert(
                        alert_id=self.alert_id,
                        actor_id=actor_id,
                    )

        self.repository.acknowledge.assert_not_called()

    def test_12_acknowledged_alert_is_not_recovered_by_response_mapping(self):
        acknowledged = self.make_alert(
            status="ACKNOWLEDGED",
            acknowledged_by=self.actor_id,
            acknowledged_at=self.now,
            recovered_at=None,
        )

        result = self.service._alert_response(acknowledged)

        self.assertEqual(result["status"], "ACKNOWLEDGED")
        self.assertIsNotNone(result["acknowledged_at"])
        self.assertIsNone(result["recovered_at"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
