
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from dotenv import dotenv_values
from sqlalchemy import create_engine, func, select, text

from src.domain.models.alert import Alert
from src.domain.exceptions import ResourceConflictError
from src.infrastructure.databases.database import Database
from src.infrastructure.models import AlertHistoryModel, AlertModel
from src.infrastructure.repositories.alert_repository import (
    SqlAlchemyAlertRepository,
)


class TestAlertRepository(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        env_path = Path(__file__).resolve().parents[1] / ".env"
        database_url = dotenv_values(env_path).get("DATABASE_URL")

        if not database_url:
            raise RuntimeError(
                "Không tìm thấy DATABASE_URL trong file .env."
            )

        engine = create_engine(database_url)

        try:
            with engine.connect() as connection:
                database_name = connection.execute(
                    text("SELECT current_database()")
                ).scalar_one()

                if database_name != "arimms_python_local":
                    raise RuntimeError(
                        "Chỉ chạy test trên arimms_python_local, "
                        f"hiện tại: {database_name}"
                    )

                cls.node_id = connection.execute(
                    text("""
                        SELECT id
                        FROM nodes
                        WHERE code = 'DEMO-NODE-01'
                        LIMIT 1
                    """)
                ).scalar_one_or_none()

                cls.operator_id = connection.execute(
                    text("""
                        SELECT id
                        FROM users
                        WHERE email = 'operator@arimms.local'
                          AND role_code = 'Operator'
                          AND is_active = TRUE
                        LIMIT 1
                    """)
                ).scalar_one_or_none()

                if cls.node_id is None:
                    raise RuntimeError(
                        "Không tìm thấy Node DEMO-NODE-01."
                    )

                if cls.operator_id is None:
                    raise RuntimeError(
                        "Không tìm thấy tài khoản Operator hợp lệ."
                    )

        finally:
            engine.dispose()

        cls.database = Database(database_url)
        cls.repository = SqlAlchemyAlertRepository(
            cls.database.create_session
        )

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "database"):
            cls.database.dispose()

    def setUp(self):
        self.created_alert_ids = set()
        self.now = datetime.now(timezone.utc)

    def tearDown(self):
        if not self.created_alert_ids:
            return

        with self.database.create_session() as session:
            session.query(AlertHistoryModel).filter(
                AlertHistoryModel.alert_id.in_(
                    self.created_alert_ids
                )
            ).delete(synchronize_session=False)

            session.query(AlertModel).filter(
                AlertModel.id.in_(self.created_alert_ids)
            ).delete(synchronize_session=False)

            session.commit()

    # --------------------------------------------------
    # Test helpers
    # --------------------------------------------------

    def make_alert(
        self,
        status="FIRING",
        metric="cpu_percent",
        severity="HIGH",
        triggered_at=None,
        triggered_value=95.5,
    ):
        alert = Alert(
            id=str(uuid4()),
            node_id=str(self.node_id),
            rule_id=None,
            metric=metric,
            operator=">=",
            threshold=80.0,
            severity=severity,
            status=status,
            message="Repository integration test",
            triggered_at=triggered_at or self.now,
            acknowledged_at=None,
            recovered_at=None,
            triggered_value=triggered_value,
            acknowledged_by=None,
        )

        saved = self.repository.save(alert)
        self.created_alert_ids.add(saved.id)

        return saved

    def count_history(self, alert_id):
        with self.database.create_session() as session:
            return session.execute(
                select(func.count())
                .select_from(AlertHistoryModel)
                .where(
                    AlertHistoryModel.alert_id == alert_id
                )
            ).scalar_one()

    # --------------------------------------------------
    # Save and detail
    # --------------------------------------------------

    def test_01_save_and_find_alert(self):
        saved = self.make_alert()

        found = self.repository.find_by_id(saved.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, saved.id)
        self.assertEqual(found.node_id, str(self.node_id))
        self.assertEqual(found.triggered_value, 95.5)
        self.assertEqual(found.status, "FIRING")
        self.assertIsNone(found.acknowledged_by)
        self.assertIsNone(found.acknowledged_at)

    def test_02_find_missing_alert_returns_none(self):
        result = self.repository.find_by_id(str(uuid4()))

        self.assertIsNone(result)

    # --------------------------------------------------
    # Filters and pagination
    # --------------------------------------------------

    def test_03_query_filters(self):
        matching = self.make_alert(
            metric="cpu_percent",
            severity="HIGH",
            status="FIRING",
        )

        self.make_alert(
            metric="memory_percent",
            severity="HIGH",
            status="FIRING",
        )

        self.make_alert(
            metric="cpu_percent",
            severity="LOW",
            status="FIRING",
        )

        self.make_alert(
            metric="cpu_percent",
            severity="HIGH",
            status="RECOVERED",
        )

        items, total = self.repository.query_alerts(
            node_id=str(self.node_id),
            metric="cpu_percent",
            severity="HIGH",
            status="FIRING",
        )

        result_ids = {item.id for item in items}

        self.assertEqual(total, 1)
        self.assertEqual(result_ids, {matching.id})

    def test_04_query_time_range(self):
        inside = self.make_alert(
            triggered_at=self.now - timedelta(hours=1)
        )

        self.make_alert(
            triggered_at=self.now - timedelta(days=2)
        )

        self.make_alert(
            triggered_at=self.now + timedelta(hours=2)
        )

        items, total = self.repository.query_alerts(
            start_time=self.now - timedelta(hours=2),
            end_time=self.now,
        )

        self.assertEqual(total, 1)
        self.assertEqual(items[0].id, inside.id)

    def test_05_query_pagination_and_order(self):
        alerts = [
            self.make_alert(
                triggered_at=self.now - timedelta(minutes=i)
            )
            for i in range(5)
        ]

        first_page, total = self.repository.query_alerts(
            node_id=str(self.node_id),
            page=1,
            page_size=2,
        )

        second_page, second_total = self.repository.query_alerts(
            node_id=str(self.node_id),
            page=2,
            page_size=2,
        )

        self.assertEqual(total, 5)
        self.assertEqual(total, second_total)
        self.assertEqual(len(first_page), 2)
        self.assertEqual(len(second_page), 2)

        self.assertEqual(first_page[0].id, alerts[0].id)
        self.assertEqual(first_page[1].id, alerts[1].id)

        first_ids = {item.id for item in first_page}
        second_ids = {item.id for item in second_page}

        self.assertTrue(first_ids.isdisjoint(second_ids))

    def test_06_query_rejects_invalid_input(self):
        invalid_calls = [
            {"node_id": "not-a-uuid"},
            {"metric": "invalid_metric"},
            {"severity": "INVALID"},
            {"status": "INVALID"},
            {"page": 0},
            {"page_size": 101},
            {"start_time": "2026-11-24"},
            {
                "start_time": self.now,
                "end_time": self.now - timedelta(days=1),
            },
        ]

        for kwargs in invalid_calls:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(Exception):
                    self.repository.query_alerts(**kwargs)

    # --------------------------------------------------
    # Acknowledgement
    # --------------------------------------------------

    def test_07_acknowledge_records_history_without_recovery(self):
        alert = self.make_alert()

        acknowledged_at = self.now + timedelta(seconds=5)

        result = self.repository.acknowledge(
            alert.id,
            str(self.operator_id),
            acknowledged_at,
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.status, "ACKNOWLEDGED")

        self.assertEqual(
            result.acknowledged_by,
            str(self.operator_id),
        )

        self.assertEqual(
            result.acknowledged_at,
            acknowledged_at,
        )

        # Acknowledgement must not mark the alert as recovered.
        self.assertIsNone(result.recovered_at)

        self.assertEqual(
            self.count_history(alert.id),
            1,
        )

        with self.database.create_session() as session:
            history = session.execute(
                select(AlertHistoryModel).where(
                    AlertHistoryModel.alert_id == alert.id
                )
            ).scalar_one()

            self.assertEqual(
                history.actor_id,
                str(self.operator_id),
            )

            self.assertEqual(
                history.action,
                "ACKNOWLEDGE",
            )

            self.assertEqual(
                history.from_status,
                "FIRING",
            )

            self.assertEqual(
                history.to_status,
                "ACKNOWLEDGED",
            )

    def test_08_repeated_acknowledgement_is_idempotent(self):
        alert = self.make_alert()

        first_time = self.now + timedelta(seconds=5)
        second_time = self.now + timedelta(seconds=10)

        first = self.repository.acknowledge(
            alert.id,
            str(self.operator_id),
            first_time,
        )

        second = self.repository.acknowledge(
            alert.id,
            str(self.operator_id),
            second_time,
        )

        self.assertEqual(first.status, "ACKNOWLEDGED")
        self.assertEqual(second.status, "ACKNOWLEDGED")

        # Repeated acknowledgement must not overwrite the first time.
        self.assertEqual(
            second.acknowledged_at,
            first_time,
        )

        # Only one history record should be created.
        self.assertEqual(
            self.count_history(alert.id),
            1,
        )

    def test_09_recovered_alert_cannot_be_acknowledged(self):
        alert = self.make_alert(status="RECOVERED")

        with self.assertRaises(ResourceConflictError):
            self.repository.acknowledge(
                alert.id,
                str(self.operator_id),
                self.now,
            )

        unchanged = self.repository.find_by_id(alert.id)

        self.assertEqual(
            unchanged.status,
            "RECOVERED",
        )

        self.assertIsNone(unchanged.acknowledged_at)

        self.assertEqual(
            self.count_history(alert.id),
            0,
        )

    def test_10_missing_alert_acknowledgement_returns_none(self):
        result = self.repository.acknowledge(
            str(uuid4()),
            str(self.operator_id),
            self.now,
        )

        self.assertIsNone(result)

    def test_11_invalid_acknowledgement_input(self):
        alert = self.make_alert()

        with self.assertRaises(Exception):
            self.repository.acknowledge(
                alert.id,
                "invalid-actor-id",
                self.now,
            )

        with self.assertRaises(Exception):
            self.repository.acknowledge(
                alert.id,
                str(self.operator_id),
                datetime.now(),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
