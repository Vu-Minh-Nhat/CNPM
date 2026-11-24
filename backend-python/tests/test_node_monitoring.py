import unittest
from datetime import datetime, timedelta, timezone

from src.domain.exceptions import ValidationError
from src.domain.models.node_monitoring import (
    evaluate_node_monitoring,
)


class TestNodeMonitoring(unittest.TestCase):
    def setUp(self):
        self.now = datetime(
            2026, 11, 17, 12, 0, 0,
            tzinfo=timezone.utc,
        )

    def evaluate(self, **changes):
        arguments = {
            "now": self.now,
            "last_received_at": self.now,
            "last_measured_at": self.now,
        }
        arguments.update(changes)

        return evaluate_node_monitoring(**arguments)

    def test_01_never_received_data(self):
        state = self.evaluate(
            last_received_at=None,
            last_measured_at=None,
        )

        self.assertEqual(state.connection_status, "never_seen")
        self.assertEqual(state.data_status, "no_data")
        self.assertIsNone(state.seconds_since_received)
        self.assertIsNone(state.seconds_since_measured)

    def test_02_data_freshness_boundary(self):
        cases = (
            (29, "fresh"),
            (30, "fresh"),
            (30.001, "stale"),
            (31, "stale"),
        )

        for age, expected in cases:
            with self.subTest(age=age):
                state = self.evaluate(
                    last_measured_at=(
                        self.now - timedelta(seconds=age)
                    )
                )

                self.assertEqual(state.data_status, expected)
                self.assertEqual(
                    state.connection_status, "online"
                )

    def test_03_connection_boundary(self):
        cases = (
            (89, "online"),
            (90, "online"),
            (90.001, "offline"),
            (91, "offline"),
        )

        for age, expected in cases:
            with self.subTest(age=age):
                timestamp = self.now - timedelta(seconds=age)

                state = self.evaluate(
                    last_received_at=timestamp,
                    last_measured_at=timestamp,
                )

                self.assertEqual(
                    state.connection_status, expected
                )
                self.assertEqual(state.data_status, "stale")

    def test_04_old_sample_received_recently(self):
        state = self.evaluate(
            last_received_at=(
                self.now - timedelta(seconds=1)
            ),
            last_measured_at=(
                self.now - timedelta(minutes=5)
            ),
        )

        self.assertEqual(state.connection_status, "online")
        self.assertEqual(state.data_status, "stale")
        self.assertEqual(state.seconds_since_received, 1)
        self.assertEqual(state.seconds_since_measured, 300)

    def test_05_time_passes_without_new_data(self):
        initial = self.evaluate()

        later = self.evaluate(
            now=self.now + timedelta(seconds=91)
        )

        self.assertEqual(initial.connection_status, "online")
        self.assertEqual(initial.data_status, "fresh")

        self.assertEqual(later.connection_status, "offline")
        self.assertEqual(later.data_status, "stale")

    def test_06_receiving_new_sample_restores_status(self):
        old_time = self.now - timedelta(seconds=120)

        before = self.evaluate(
            last_received_at=old_time,
            last_measured_at=old_time,
        )
        after = self.evaluate(
            last_received_at=self.now,
            last_measured_at=self.now,
        )

        self.assertEqual(before.connection_status, "offline")
        self.assertEqual(before.data_status, "stale")

        self.assertEqual(after.connection_status, "online")
        self.assertEqual(after.data_status, "fresh")

    def test_07_different_timezones(self):
        vietnam_timezone = timezone(timedelta(hours=7))

        state = self.evaluate(
            last_received_at=(
                self.now - timedelta(seconds=10)
            ).astimezone(vietnam_timezone),
            last_measured_at=(
                self.now - timedelta(seconds=20)
            ).astimezone(vietnam_timezone),
        )

        self.assertEqual(state.connection_status, "online")
        self.assertEqual(state.data_status, "fresh")
        self.assertEqual(state.seconds_since_received, 10)
        self.assertEqual(state.seconds_since_measured, 20)

    def test_08_naive_timestamps_rejected(self):
        naive_time = self.now.replace(tzinfo=None)

        for field in (
            "now",
            "last_received_at",
            "last_measured_at",
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValidationError):
                    self.evaluate(**{field: naive_time})

    def test_09_threshold_configuration(self):
        timestamp = self.now - timedelta(seconds=100)

        state = self.evaluate(
            last_received_at=timestamp,
            last_measured_at=timestamp,
            stale_after_seconds=120,
            offline_after_seconds=180,
        )

        self.assertEqual(state.connection_status, "online")
        self.assertEqual(state.data_status, "fresh")

        for field in (
            "stale_after_seconds",
            "offline_after_seconds",
        ):
            for value in (0, -1, True, "30", None, 1.5):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValidationError):
                        self.evaluate(**{field: value})

    def test_10_future_timestamps(self):
        future = self.now + timedelta(seconds=10)

        received_in_future = self.evaluate(
            last_received_at=future,
        )
        measured_in_future = self.evaluate(
            last_measured_at=future,
        )

        self.assertEqual(
            received_in_future.connection_status,
            "unknown",
        )
        self.assertEqual(
            measured_in_future.data_status,
            "invalid_time",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)