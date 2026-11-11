import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Barrier
from uuid import uuid4

from dotenv import dotenv_values
from sqlalchemy import delete, func, insert, select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError

from src.domain.exceptions import (
    ResourceConflictError,
    ValidationError,
)
from src.domain.models.telemetry import TelemetrySample
from src.infrastructure.databases.database import Database
from src.infrastructure.models import NodeModel, TelemetryModel
from src.infrastructure.repositories.telemetry_repository import (
    SqlAlchemyTelemetryRepository,
)


class TestTelemetryRepository(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        backend_root = Path(__file__).resolve().parents[1]
        settings = dotenv_values(backend_root / ".env.migration")
        database_url = settings.get("DATABASE_URL")

        if (
            not database_url
            or make_url(database_url).database != "arimms_python_check"
        ):
            raise RuntimeError(
                "Kiểm thử yêu cầu database arimms_python_check."
            )

        cls.database = Database(database_url)
        cls.addClassCleanup(cls.database.dispose)

    def setUp(self):
        self.repository = SqlAlchemyTelemetryRepository(
            self.database.create_session
        )
        self.test_nodes = []
        self.addCleanup(self._cleanup)

        self.node_id = self._create_node()
        self.base_time = datetime(
            2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc
        )

    def _create_node(self):
        node_id = str(uuid4())
        code = f"AI43-{uuid4().hex}"

        with self.database.create_session() as session:
            with session.begin():
                seed_node = session.scalar(
                    select(NodeModel).where(
                        NodeModel.code == "DEMO-NODE-01"
                    )
                )

                if seed_node is None:
                    raise RuntimeError(
                        "Cần seed DEMO-NODE-01 trước khi chạy test."
                    )

                session.add(NodeModel(
                    id=node_id,
                    rack_id=seed_node.rack_id,
                    code=code,
                    name="AI-43 test node",
                    serial_number=None,
                ))

        self.test_nodes.append((node_id, code))
        return node_id

    def _cleanup(self):
        with self.database.create_session() as session:
            with session.begin():
                for node_id, expected_code in reversed(self.test_nodes):
                    node = session.get(NodeModel, node_id)

                    if node is None:
                        continue

                    if node.code != expected_code:
                        raise RuntimeError(
                            "Node không khớp dữ liệu test. Dừng dọn."
                        )

                    session.execute(
                        delete(TelemetryModel).where(
                            TelemetryModel.node_id == node_id
                        )
                    )
                    session.execute(
                        delete(NodeModel).where(
                            NodeModel.id == node_id,
                            NodeModel.code == expected_code,
                        )
                    )

    def _sample(self, **changes):
        sample = TelemetrySample(
            message_id=str(uuid4()),
            node_id=self.node_id,
            measured_at=self.base_time,
            cpu_percent=10.5,
            memory_percent=20.5,
            disk_percent=30.5,
        )
        return replace(sample, **changes)

    def _count(self, node_id=None):
        with self.database.create_session() as session:
            return session.scalar(
                select(func.count())
                .select_from(TelemetryModel)
                .where(
                    TelemetryModel.node_id == (
                        self.node_id if node_id is None else node_id
                    )
                )
            )

    def _assert_database_rejects(self, overrides, expected_state):
        values = {
            "id": str(uuid4()),
            **asdict(self._sample()),
            **overrides,
        }

        with self.database.engine.connect() as connection:
            transaction = connection.begin()

            try:
                with self.assertRaises(IntegrityError) as caught:
                    connection.execute(
                        insert(TelemetryModel).values(**values)
                    )

                self.assertEqual(
                    caught.exception.orig.sqlstate,
                    expected_state,
                )
            finally:
                transaction.rollback()

    def test_01_save_valid_sample(self):
        sample = self._sample()
        result = self.repository.save(sample)

        self.assertTrue(result.id)
        self.assertEqual(result.node_id, self.node_id)
        self.assertEqual(result.message_id, sample.message_id)
        self.assertEqual(result.measured_at, sample.measured_at)
        self.assertEqual(result.cpu_percent, 10.5)
        self.assertIsNotNone(result.received_at.utcoffset())
        self.assertEqual(self._count(), 1)

    def test_02_resend_returns_existing_record(self):
        sample = self._sample()

        first = self.repository.save(sample)
        second = self.repository.save(sample)

        self.assertEqual(first, second)
        self.assertEqual(self._count(), 1)

    def test_03_conflicting_payload_does_not_overwrite(self):
        sample = self._sample()
        original = self.repository.save(sample)

        with self.assertRaises(ResourceConflictError):
            self.repository.save(
                replace(sample, cpu_percent=99.0)
            )

        stored = self.repository.get_latest(self.node_id)

        self.assertEqual(stored, original)
        self.assertEqual(self._count(), 1)

    def test_04_missing_node_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.repository.save(
                self._sample(node_id=str(uuid4()))
            )

        self.assertEqual(self._count(), 0)

    def test_05_invalid_metrics_are_rejected(self):
        invalid_values = (
            -1,
            101,
            float("nan"),
            float("inf"),
            True,
            "10",
            None,
        )

        for field in (
            "cpu_percent",
            "memory_percent",
            "disk_percent",
        ):
            for value in invalid_values:
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValidationError):
                        self.repository.save(
                            self._sample(**{field: value})
                        )

        self.assertEqual(self._count(), 0)

    def test_06_naive_timestamp_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.repository.save(
                self._sample(
                    measured_at=self.base_time.replace(tzinfo=None)
                )
            )

        self.assertEqual(self._count(), 0)

    def test_07_latest_uses_measurement_time(self):
        newer = self.repository.save(
            self._sample(
                measured_at=self.base_time + timedelta(minutes=2)
            )
        )

        # Mẫu cũ đến sau không được trở thành mẫu đo mới nhất.
        self.repository.save(
            self._sample(measured_at=self.base_time)
        )

        latest = self.repository.get_latest(self.node_id)

        self.assertEqual(latest.id, newer.id)

    def test_08_history_range_order_and_limit(self):
        records = []

        for minute in range(5):
            records.append(
                self.repository.save(
                    self._sample(
                        measured_at=(
                            self.base_time + timedelta(minutes=minute)
                        )
                    )
                )
            )

        start = self.base_time + timedelta(minutes=1)
        end = self.base_time + timedelta(minutes=4)

        history = self.repository.list_history(
            self.node_id,
            start=start,
            end=end,
        )

        self.assertEqual(
            [record.id for record in history],
            [record.id for record in records[1:4]],
        )

        limited = self.repository.list_history(
            self.node_id,
            start=start,
            end=end,
            limit=2,
        )

        self.assertEqual(
            [record.id for record in limited],
            [record.id for record in records[1:3]],
        )

    def test_09_node_isolation_and_empty_result(self):
        other_node_id = self._create_node()

        self.assertIsNone(
            self.repository.get_latest(other_node_id)
        )
        self.assertEqual(
            self.repository.list_history(
                other_node_id,
                start=self.base_time,
                end=self.base_time + timedelta(hours=1),
            ),
            [],
        )

        sample = self._sample()
        first = self.repository.save(sample)

        # Cùng message_id nhưng khác Node được phép lưu.
        second = self.repository.save(
            replace(sample, node_id=other_node_id)
        )

        self.assertNotEqual(first.id, second.id)
        self.assertEqual(
            self.repository.get_latest(self.node_id).id,
            first.id,
        )
        self.assertEqual(
            self.repository.get_latest(other_node_id).id,
            second.id,
        )

        history = self.repository.list_history(
            self.node_id,
            start=self.base_time,
            end=self.base_time + timedelta(hours=1),
        )
        self.assertEqual([record.id for record in history], [first.id])

    def test_10_database_foreign_key(self):
        self._assert_database_rejects(
            {"node_id": str(uuid4())},
            "23503",
        )

    def test_11_database_metric_constraints(self):
        for field in (
            "cpu_percent",
            "memory_percent",
            "disk_percent",
        ):
            with self.subTest(field=field):
                self._assert_database_rejects(
                    {field: 101},
                    "23514",
                )

    def test_12_database_unique_constraint(self):
        sample = self._sample()
        self.repository.save(sample)

        self._assert_database_rejects(
            {"message_id": sample.message_id},
            "23505",
        )

        self.assertEqual(self._count(), 1)

    def test_13_query_validation(self):
        end = self.base_time + timedelta(hours=1)

        with self.assertRaises(ValidationError):
            self.repository.get_latest("not-a-uuid")

        with self.assertRaises(ValidationError):
            self.repository.list_history(
                self.node_id,
                start=end,
                end=self.base_time,
            )

        with self.assertRaises(ValidationError):
            self.repository.list_history(
                self.node_id,
                start=self.base_time.replace(tzinfo=None),
                end=end,
            )

        for limit in (0, 1001, True):
            with self.subTest(limit=limit):
                with self.assertRaises(ValidationError):
                    self.repository.list_history(
                        self.node_id,
                        start=self.base_time,
                        end=end,
                        limit=limit,
                    )

    def test_14_concurrent_resend(self):
        sample = self._sample()
        barrier = Barrier(2)

        def save_same_sample():
            barrier.wait(timeout=10)
            return self.repository.save(sample)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(save_same_sample)
                for _ in range(2)
            ]
            results = [future.result() for future in futures]

        self.assertEqual(results[0].id, results[1].id)
        self.assertEqual(self._count(), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)