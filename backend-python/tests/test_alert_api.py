
import getpass
import os
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from dotenv import dotenv_values
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url

from src.create_app import create_app
from src.domain.models.alert import Alert
from src.infrastructure.databases.database import Database
from src.infrastructure.models import AlertHistoryModel, AlertModel
from src.infrastructure.repositories.alert_repository import (
    SqlAlchemyAlertRepository,
)


class TestAlertAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        backend_root = Path(__file__).resolve().parents[1]
        settings = dotenv_values(backend_root / ".env")
        database_url = settings.get("DATABASE_URL")

        if not database_url:
            raise RuntimeError(
                "Không tìm thấy DATABASE_URL trong file .env."
            )

        if make_url(database_url).database != "arimms_python_local":
            raise RuntimeError(
                "Alert API tests chỉ được chạy trên "
                "arimms_python_local."
            )

        os.environ["DATABASE_URL"] = database_url

        # Kiểm tra dữ liệu seed trước khi khởi tạo API.
        engine = create_engine(database_url)

        try:
            with engine.connect() as connection:
                cls.database_name = connection.execute(
                    text("SELECT current_database()")
                ).scalar_one()

                cls.node_id = connection.execute(
                    text("""
                        SELECT id
                        FROM nodes
                        WHERE code = 'DEMO-NODE-01'
                        LIMIT 1
                    """)
                ).scalar_one_or_none()

                accounts = connection.execute(
                    text("""
                        SELECT id, email, role_code
                        FROM users
                        WHERE email IN (
                            'admin@arimms.local',
                            'operator@arimms.local',
                            'tech@arimms.local'
                        )
                        AND is_active = TRUE
                    """)
                ).all()

                cls.account_ids = {
                    row.role_code: str(row.id)
                    for row in accounts
                }

        finally:
            engine.dispose()

        if cls.node_id is None:
            raise RuntimeError(
                "Không tìm thấy Node DEMO-NODE-01."
            )

        expected_roles = {
            "Administrator",
            "Operator",
            "Technician",
        }

        if set(cls.account_ids) != expected_roles:
            raise RuntimeError(
                "Thiếu tài khoản seed Administrator, Operator "
                "hoặc Technician."
            )

        # Khởi tạo Flask API trên database local.
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.addClassCleanup(
            cls.app.extensions["database"].dispose
        )

        cls.client = cls.app.test_client()

        # Repository dùng để tạo và dọn Alert do test tạo.
        cls.database = Database(database_url)
        cls.repository = SqlAlchemyAlertRepository(
            cls.database.create_session
        )
        cls.addClassCleanup(cls.database.dispose)

        # Đăng nhập cả ba vai trò.
        password = getpass.getpass(
            "Nhập mật khẩu chung của 3 tài khoản seed "
            "trong arimms_python_local: "
        )

        cls.headers_by_role = {}

        accounts_by_role = {
            "Administrator": "admin@arimms.local",
            "Operator": "operator@arimms.local",
            "Technician": "tech@arimms.local",
        }

        for role, email in accounts_by_role.items():
            response = cls.client.post(
                "/auth/login",
                json={
                    "email": email,
                    "password": password,
                },
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"Không đăng nhập được tài khoản {email}. "
                    f"HTTP {response.status_code}: "
                    f"{response.get_json()}"
                )

            data = response.get_json()

            if (
                data.get("role") != role
                or not data.get("accessToken")
            ):
                raise RuntimeError(
                    f"Phản hồi đăng nhập không hợp lệ: {email}"
                )

            cls.headers_by_role[role] = {
                "Authorization": (
                    f"Bearer {data['accessToken']}"
                )
            }

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
                AlertModel.id.in_(
                    self.created_alert_ids
                )
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
    ):
        triggered_at = triggered_at or self.now

        alert = Alert(
            id=str(uuid4()),
            node_id=str(self.node_id),
            rule_id=None,
            metric=metric,
            operator=">=",
            threshold=80.0,
            severity=severity,
            status=status,
            message="Alert API integration test",
            triggered_at=triggered_at,
            acknowledged_at=None,
            recovered_at=(
                triggered_at
                if status == "RECOVERED"
                else None
            ),
            triggered_value=95.5,
            acknowledged_by=None,
        )

        saved = self.repository.save(alert)
        self.created_alert_ids.add(saved.id)

        return saved

    def headers(self, role):
        return self.headers_by_role[role]

    # --------------------------------------------------
    # List API
    # --------------------------------------------------

    def test_01_all_roles_can_list_alerts(self):
        alert = self.make_alert()

        for role in (
            "Administrator",
            "Operator",
            "Technician",
        ):
            with self.subTest(role=role):
                response = self.client.get(
                    "/alerts",
                    headers=self.headers(role),
                )

                self.assertEqual(
                    response.status_code,
                    200,
                )

                data = response.get_json()

                self.assertIn("items", data)
                self.assertIn("pagination", data)

                result_ids = {
                    item["id"]
                    for item in data["items"]
                }

                self.assertIn(alert.id, result_ids)

    def test_02_list_alerts_supports_filters_and_pagination(self):
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

        response = self.client.get(
            "/alerts",
            query_string={
                "node_id": str(self.node_id),
                "metric": "cpu_percent",
                "severity": "HIGH",
                "status": "FIRING",
                "start_time": (
                    self.now - timedelta(seconds=5)
                ).isoformat(),
                "end_time": (
                    self.now + timedelta(seconds=5)
                ).isoformat(),
                "page": 1,
                "page_size": 1,
            },
            headers=self.headers("Administrator"),
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(
            data["items"][0]["id"],
            matching.id,
        )

        pagination = data["pagination"]

        self.assertEqual(pagination["page"], 1)
        self.assertEqual(pagination["page_size"], 1)
        self.assertGreaterEqual(pagination["total"], 1)

    def test_03_invalid_list_parameters_return_400(self):
        invalid_queries = [
            {"page": "invalid"},
            {"page": "0"},
            {"page_size": "101"},
            {"metric": "invalid_metric"},
            {"severity": "INVALID"},
            {"status": "INVALID"},
            {"start_time": "not-a-timestamp"},
            {
                "start_time": "2026-11-24T10:00:00",
            },
        ]

        for query in invalid_queries:
            with self.subTest(query=query):
                response = self.client.get(
                    "/alerts",
                    query_string=query,
                    headers=self.headers("Administrator"),
                )

                self.assertEqual(
                    response.status_code,
                    400,
                )

    # --------------------------------------------------
    # Detail API
    # --------------------------------------------------

    def test_04_all_roles_can_get_alert_detail(self):
        alert = self.make_alert()

        for role in (
            "Administrator",
            "Operator",
            "Technician",
        ):
            with self.subTest(role=role):
                response = self.client.get(
                    f"/alerts/{alert.id}",
                    headers=self.headers(role),
                )

                self.assertEqual(
                    response.status_code,
                    200,
                )

                data = response.get_json()

                self.assertEqual(data["id"], alert.id)
                self.assertEqual(
                    data["node_id"],
                    str(self.node_id),
                )
                self.assertEqual(
                    data["triggered_value"],
                    95.5,
                )
                self.assertEqual(data["status"], "FIRING")
                self.assertIsNone(data["acknowledged_at"])
                self.assertIsNone(data["recovered_at"])

    # --------------------------------------------------
    # Acknowledge API and RBAC
    # --------------------------------------------------

    def test_05_admin_and_operator_can_acknowledge(self):
        alert = self.make_alert()

        # Administrator thực hiện acknowledge lần đầu.
        admin_response = self.client.post(
            f"/alerts/{alert.id}/acknowledge",
            headers=self.headers("Administrator"),
        )

        self.assertEqual(
            admin_response.status_code,
            200,
        )

        admin_data = admin_response.get_json()

        self.assertEqual(
            admin_data["status"],
            "ACKNOWLEDGED",
        )

        self.assertEqual(
            admin_data["acknowledged_by"],
            self.account_ids["Administrator"],
        )

        self.assertIsNotNone(
            admin_data["acknowledged_at"]
        )

        # Acknowledge không đồng nghĩa với recovery.
        self.assertIsNone(
            admin_data["recovered_at"]
        )

        # Operator được phép gọi lại; thao tác idempotent.
        operator_response = self.client.post(
            f"/alerts/{alert.id}/acknowledge",
            headers=self.headers("Operator"),
        )

        self.assertEqual(
            operator_response.status_code,
            200,
        )

        operator_data = operator_response.get_json()

        self.assertEqual(
            operator_data["status"],
            "ACKNOWLEDGED",
        )

        # Không ghi đè người xác nhận đầu tiên.
        self.assertEqual(
            operator_data["acknowledged_by"],
            self.account_ids["Administrator"],
        )

        self.assertEqual(
            operator_data["acknowledged_at"],
            admin_data["acknowledged_at"],
        )

    def test_06_technician_cannot_acknowledge(self):
        alert = self.make_alert()

        response = self.client.post(
            f"/alerts/{alert.id}/acknowledge",
            headers=self.headers("Technician"),
        )

        self.assertEqual(response.status_code, 403)

        unchanged = self.repository.find_by_id(alert.id)

        self.assertEqual(unchanged.status, "FIRING")
        self.assertIsNone(unchanged.acknowledged_by)
        self.assertIsNone(unchanged.acknowledged_at)

    def test_07_recovered_alert_returns_conflict(self):
        alert = self.make_alert(status="RECOVERED")

        response = self.client.post(
            f"/alerts/{alert.id}/acknowledge",
            headers=self.headers("Administrator"),
        )

        self.assertEqual(response.status_code, 409)

        unchanged = self.repository.find_by_id(alert.id)

        self.assertEqual(unchanged.status, "RECOVERED")
        self.assertIsNone(unchanged.acknowledged_at)

    # --------------------------------------------------
    # Authentication and not found
    # --------------------------------------------------

    def test_08_missing_token_returns_401(self):
        alert = self.make_alert()

        requests = [
            ("GET", "/alerts"),
            ("GET", f"/alerts/{alert.id}"),
            (
                "POST",
                f"/alerts/{alert.id}/acknowledge",
            ),
        ]

        for method, path in requests:
            with self.subTest(method=method, path=path):
                response = self.client.open(
                    path,
                    method=method,
                )

                self.assertEqual(
                    response.status_code,
                    401,
                )

    def test_09_invalid_token_returns_401(self):
        headers = {
            "Authorization": "Bearer invalid-token"
        }

        alert = self.make_alert()

        requests = [
            ("GET", "/alerts"),
            ("GET", f"/alerts/{alert.id}"),
            (
                "POST",
                f"/alerts/{alert.id}/acknowledge",
            ),
        ]

        for method, path in requests:
            with self.subTest(method=method, path=path):
                response = self.client.open(
                    path,
                    method=method,
                    headers=headers,
                )

                self.assertEqual(
                    response.status_code,
                    401,
                )

    def test_10_missing_alert_returns_404(self):
        missing_id = str(uuid4())
        headers = self.headers("Administrator")

        detail_response = self.client.get(
            f"/alerts/{missing_id}",
            headers=headers,
        )

        self.assertEqual(
            detail_response.status_code,
            404,
        )

        acknowledge_response = self.client.post(
            f"/alerts/{missing_id}/acknowledge",
            headers=headers,
        )

        self.assertEqual(
            acknowledge_response.status_code,
            404,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
