
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from src.domain.exceptions import ResourceConflictError
from src.domain.models.alert import Alert
from src.domain.models.alert_rule import AlertRule
from src.domain.models.telemetry import TelemetryRecord
from src.services.alert_detector import AlertDetector


class TestAlertDetector(unittest.TestCase):

    def setUp(self):
        self.now = datetime(2026, 11, 24, 10, 0, 0, tzinfo=timezone.utc)
        self.node_id = str(uuid4())
        self.rule_id = str(uuid4())

        self.alert_repository = MagicMock()
        self.telemetry_repository = MagicMock()
        self.server_repository = MagicMock()

        self.alert_repository.list_active_rules.return_value = []
        self.alert_repository.find_active_by_node_and_rule.return_value = None

        self.detector = AlertDetector(
            alert_repository=self.alert_repository,
            telemetry_repository=self.telemetry_repository,
            server_repository=self.server_repository,
            stale_after_seconds=30,
            offline_after_seconds=90,
        )

    def make_rule(
        self,
        metric="cpu_percent",
        operator=">=",
        threshold=80,
        recovery_operator="<=",
        recovery_threshold=70,
        is_active=True,
    ):
        return AlertRule(
            id=self.rule_id,
            metric=metric,
            operator=operator,
            threshold=threshold,
            severity="HIGH",
            recovery_operator=recovery_operator,
            recovery_threshold=recovery_threshold,
            is_active=is_active,
            created_at=self.now - timedelta(days=1),
            updated_at=self.now - timedelta(days=1),
        )

    def make_telemetry(
        self,
        cpu=50,
        memory=50,
        disk=50,
        measured_age=10,
        received_age=10,
    ):
        return TelemetryRecord(
            message_id=str(uuid4()),
            node_id=self.node_id,
            measured_at=self.now - timedelta(seconds=measured_age),
            cpu_percent=cpu,
            memory_percent=memory,
            disk_percent=disk,
            id=str(uuid4()),
            received_at=self.now - timedelta(seconds=received_age),
        )

    def make_alert(self, metric="cpu_percent"):
        return Alert(
            id=str(uuid4()),
            node_id=self.node_id,
            rule_id=self.rule_id,
            metric=metric,
            operator=">=",
            threshold=80,
            severity="HIGH",
            status="FIRING",
            message="Test alert",
            triggered_at=self.now - timedelta(minutes=1),
            acknowledged_at=None,
            recovered_at=None,
        )

    def evaluate(self, rule, telemetry=None, last_received_at=None):
        self.telemetry_repository.get_latest.return_value = telemetry
        self.telemetry_repository.get_last_received_at.return_value = (
            last_received_at
        )

        return self.detector.evaluate_node(
            node_id=self.node_id,
            rules=[rule],
            now=self.now,
        )

    # ---------------------------------------------------------
    # 1. Threshold boundary: CPU, RAM, Disk
    # ---------------------------------------------------------

    def test_01_metrics_trigger_at_configured_threshold(self):
        metrics = [
            ("cpu_percent", 80),
            ("memory_percent", 80),
            ("disk_percent", 80),
        ]

        for metric, value in metrics:
            with self.subTest(metric=metric):
                self.alert_repository.reset_mock()
                self.alert_repository.find_active_by_node_and_rule.return_value = None

                rule = self.make_rule(
                    metric=metric,
                    operator=">=",
                    threshold=80,
                )

                telemetry = self.make_telemetry(
                    cpu=value if metric == "cpu_percent" else 50,
                    memory=value if metric == "memory_percent" else 50,
                    disk=value if metric == "disk_percent" else 50,
                )

                result = self.evaluate(
                    rule,
                    telemetry,
                    self.now - timedelta(seconds=10),
                )

                self.assertEqual(result["created"], 1)
                self.alert_repository.save.assert_called_once()

    def test_02_metric_below_threshold_does_not_trigger(self):
        rule = self.make_rule(
            metric="cpu_percent",
            operator=">=",
            threshold=80,
        )

        telemetry = self.make_telemetry(cpu=79.99)

        result = self.evaluate(
            rule,
            telemetry,
            self.now - timedelta(seconds=10),
        )

        self.assertEqual(result["created"], 0)
        self.alert_repository.save.assert_not_called()

    def test_03_strict_greater_than_does_not_trigger_at_boundary(self):
        rule = self.make_rule(
            metric="cpu_percent",
            operator=">",
            threshold=80,
        )

        telemetry = self.make_telemetry(cpu=80)

        result = self.evaluate(
            rule,
            telemetry,
            self.now - timedelta(seconds=10),
        )

        self.assertEqual(result["created"], 0)
        self.alert_repository.save.assert_not_called()

    # ---------------------------------------------------------
    # 2. Duplicate suppression
    # ---------------------------------------------------------

    def test_04_continuous_violation_does_not_create_duplicate_alert(self):
        rule = self.make_rule()
        telemetry = self.make_telemetry(cpu=90)

        active_alert = None

        def find_active(node_id, rule_id):
            return active_alert

        def save_alert(alert):
            nonlocal active_alert
            active_alert = alert
            return alert

        self.alert_repository.find_active_by_node_and_rule.side_effect = (
            find_active
        )
        self.alert_repository.save.side_effect = save_alert

        first_result = self.evaluate(
            rule,
            telemetry,
            self.now - timedelta(seconds=10),
        )

        second_result = self.evaluate(
            rule,
            telemetry,
            self.now - timedelta(seconds=10),
        )

        self.assertEqual(first_result["created"], 1)
        self.assertEqual(second_result["created"], 0)
        self.assertEqual(second_result["unchanged"], 1)
        self.assertEqual(self.alert_repository.save.call_count, 1)

    # ---------------------------------------------------------
    # 3. Recovery condition
    # ---------------------------------------------------------

    def test_05_active_alert_recovers_when_recovery_condition_is_met(self):
        rule = self.make_rule(
            metric="cpu_percent",
            operator=">=",
            threshold=80,
            recovery_operator="<=",
            recovery_threshold=70,
        )

        active_alert = self.make_alert()
        self.alert_repository.find_active_by_node_and_rule.return_value = (
            active_alert
        )
        self.alert_repository.recover.return_value = active_alert

        telemetry = self.make_telemetry(cpu=65)

        result = self.evaluate(
            rule,
            telemetry,
            self.now - timedelta(seconds=10),
        )

        self.assertEqual(result["recovered"], 1)
        self.alert_repository.recover.assert_called_once_with(
            active_alert.id,
            self.now,
        )

    def test_06_active_alert_is_not_recovered_while_condition_persists(self):
        rule = self.make_rule()
        active_alert = self.make_alert()

        self.alert_repository.find_active_by_node_and_rule.return_value = (
            active_alert
        )

        telemetry = self.make_telemetry(cpu=90)

        result = self.evaluate(
            rule,
            telemetry,
            self.now - timedelta(seconds=10),
        )

        self.assertEqual(result["unchanged"], 1)
        self.alert_repository.recover.assert_not_called()

    # ---------------------------------------------------------
    # 4. Missing and stale telemetry
    # ---------------------------------------------------------

    def test_07_missing_telemetry_does_not_create_alert(self):
        rule = self.make_rule()

        result = self.evaluate(
            rule,
            telemetry=None,
            last_received_at=None,
        )

        self.assertEqual(result["skipped"], 1)
        self.alert_repository.save.assert_not_called()

    def test_08_stale_telemetry_does_not_recover_active_alert(self):
        rule = self.make_rule()
        active_alert = self.make_alert()

        self.alert_repository.find_active_by_node_and_rule.return_value = (
            active_alert
        )

        telemetry = self.make_telemetry(
            cpu=10,
            measured_age=31,
            received_age=10,
        )

        result = self.evaluate(
            rule,
            telemetry,
            self.now - timedelta(seconds=10),
        )

        self.assertEqual(result["skipped"], 1)
        self.alert_repository.recover.assert_not_called()

    # ---------------------------------------------------------
    # 5. Node offline detection
    # ---------------------------------------------------------

    def test_09_never_seen_node_does_not_trigger_offline_alert(self):
        rule = self.make_rule(
            metric="node_offline_seconds",
            operator=">",
            threshold=90,
        )

        result = self.evaluate(
            rule,
            telemetry=None,
            last_received_at=None,
        )

        self.assertEqual(result["skipped"], 1)
        self.alert_repository.save.assert_not_called()

    def test_10_node_at_exactly_90_seconds_is_not_offline(self):
        rule = self.make_rule(
            metric="node_offline_seconds",
            operator=">",
            threshold=90,
        )

        telemetry = self.make_telemetry(
            measured_age=90,
            received_age=90,
        )

        result = self.evaluate(
            rule,
            telemetry,
            self.now - timedelta(seconds=90),
        )

        self.assertEqual(result["created"], 0)
        self.alert_repository.save.assert_not_called()

    def test_11_node_over_90_seconds_triggers_offline_alert(self):
        rule = self.make_rule(
            metric="node_offline_seconds",
            operator=">",
            threshold=90,
        )

        telemetry = self.make_telemetry(
            measured_age=91,
            received_age=91,
        )

        result = self.evaluate(
            rule,
            telemetry,
            self.now - timedelta(seconds=91),
        )

        self.assertEqual(result["created"], 1)
        self.alert_repository.save.assert_called_once()

    def test_12_node_reconnection_recovers_offline_alert(self):
        rule = self.make_rule(
            metric="node_offline_seconds",
            operator=">",
            threshold=90,
            recovery_operator="<=",
            recovery_threshold=30,
        )

        active_alert = self.make_alert(
            metric="node_offline_seconds"
        )

        self.alert_repository.find_active_by_node_and_rule.return_value = (
            active_alert
        )
        self.alert_repository.recover.return_value = active_alert

        telemetry = self.make_telemetry(
            measured_age=1,
            received_age=1,
        )

        result = self.evaluate(
            rule,
            telemetry,
            self.now - timedelta(seconds=1),
        )

        self.assertEqual(result["recovered"], 1)
        self.alert_repository.recover.assert_called_once()

    # ---------------------------------------------------------
    # 6. Concurrent conflict handling
    # ---------------------------------------------------------

    def test_13_conflict_with_existing_active_alert_does_not_duplicate(self):
        rule = self.make_rule()
        telemetry = self.make_telemetry(cpu=95)
        existing_alert = self.make_alert()

        self.alert_repository.find_active_by_node_and_rule.return_value = (
            existing_alert
        )
        self.alert_repository.save.side_effect = ResourceConflictError(
            "Active alert already exists."
        )

        result = self.evaluate(
            rule,
            telemetry,
            self.now - timedelta(seconds=10),
        )

        self.assertEqual(result["created"], 0)
        self.assertEqual(result["unchanged"], 1)

    # ---------------------------------------------------------
    # 7. Worker cycle aggregation
    # ---------------------------------------------------------

    def test_14_run_cycle_aggregates_results_from_multiple_nodes(self):
        node_1 = str(uuid4())
        node_2 = str(uuid4())

        self.server_repository.list_servers.return_value = [
            SimpleNamespace(id=node_1),
            SimpleNamespace(id=node_2),
        ]

        rule = self.make_rule()
        self.alert_repository.list_active_rules.return_value = [rule]

        telemetry_1 = TelemetryRecord(
            message_id=str(uuid4()),
            node_id=node_1,
            measured_at=self.now - timedelta(seconds=10),
            cpu_percent=90,
            memory_percent=50,
            disk_percent=50,
            id=str(uuid4()),
            received_at=self.now - timedelta(seconds=10),
        )

        telemetry_2 = TelemetryRecord(
            message_id=str(uuid4()),
            node_id=node_2,
            measured_at=self.now - timedelta(seconds=10),
            cpu_percent=20,
            memory_percent=50,
            disk_percent=50,
            id=str(uuid4()),
            received_at=self.now - timedelta(seconds=10),
        )

        self.telemetry_repository.get_latest.side_effect = [
            telemetry_1,
            telemetry_2,
        ]

        self.telemetry_repository.get_last_received_at.side_effect = [
            self.now - timedelta(seconds=10),
            self.now - timedelta(seconds=10),
        ]

        self.alert_repository.find_active_by_node_and_rule.return_value = None

        result = self.detector.run_cycle(now=self.now)

        self.assertEqual(result["nodes_checked"], 2)
        self.assertEqual(result["created"], 1)
        self.assertEqual(result["unchanged"], 1)
        self.assertEqual(self.alert_repository.save.call_count, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
