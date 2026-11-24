import getpass
import os
import unittest
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy.engine import make_url

from src.create_app import create_app


class TestBackendAPI(unittest.TestCase):
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

        os.environ["DATABASE_URL"] = database_url

        cls.app = create_app()
        cls.app.config["TESTING"] = True

        cls.addClassCleanup(
            cls.app.extensions["database"].dispose
        )

        cls.client = cls.app.test_client()
        cls.password = getpass.getpass(
            "Mật khẩu chung đã đặt khi seed database kiểm tra: "
        )

        cls.headers_by_role = {}

        accounts = {
            "Administrator": "admin@arimms.local",
            "Operator": "operator@arimms.local",
            "Technician": "tech@arimms.local",
        }

        for role, email in accounts.items():
            response = cls.client.post(
                "/auth/login",
                json={
                    "email": email,
                    "password": cls.password,
                },
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"Không đăng nhập được tài khoản seed: {email}"
                )

            data = response.get_json()

            if data.get("role") != role or not data.get("accessToken"):
                raise RuntimeError(
                    f"Phản hồi đăng nhập không hợp lệ: {email}"
                )

            cls.headers_by_role[role] = {
                "Authorization": f"Bearer {data['accessToken']}"
            }

        cls.admin_headers = cls.headers_by_role["Administrator"]

    def test_01_current_user(self):
        response = self.client.get(
            "/auth/me",
            headers=self.admin_headers,
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["email"], "admin@arimms.local")
        self.assertEqual(data["role"], "Administrator")
        self.assertTrue(data["userId"])

    def test_02_list_users(self):
        response = self.client.get(
            "/users",
            headers=self.admin_headers,
        )

        self.assertEqual(response.status_code, 200)

        users = response.get_json()
        self.assertIsInstance(users, list)

        expected_emails = {
            "admin@arimms.local",
            "operator@arimms.local",
            "tech@arimms.local",
        }
        self.assertTrue(
            expected_emails.issubset(
                {user["email"] for user in users}
            )
        )

        for user in users:
            self.assertNotIn("password", user)
            self.assertNotIn("password_hash", user)
            self.assertNotIn("passwordHash", user)

    def test_03_asset_relations(self):
        response = self.client.get(
            "/assets",
            headers=self.admin_headers,
        )

        self.assertEqual(response.status_code, 200)

        nodes = [
            node
            for node in response.get_json()
            if node["code"] == "DEMO-NODE-01"
        ]

        self.assertEqual(len(nodes), 1)
        node = nodes[0]

        self.assertEqual(node["name"], "Testbed Server")
        self.assertEqual(node["rack"]["code"], "RACK-01")
        self.assertEqual(node["rack"]["room"]["code"], "ROOM-01")
        self.assertEqual(
            node["rack"]["room"]["site"]["code"],
            "DEMO-SITE",
        )
        self.assertIn(
            "DEMO-WORKLOAD-01",
            {workload["code"] for workload in node["workloads"]},
        )

    def test_04_missing_token(self):
        for path in ("/auth/me", "/users", "/assets"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 401)

    def test_05_invalid_token(self):
        response = self.client.get(
            "/assets",
            headers={"Authorization": "Bearer invalid-token"},
        )
        self.assertEqual(response.status_code, 401)

    def test_06_account_management_forbidden(self):
        # UUID chỉ dùng làm đích kiểm tra quyền.
        target_id = "00000000-0000-0000-0000-000000000001"

        for role in ("Operator", "Technician"):
            headers = self.headers_by_role[role]

            requests = (
                ("GET", "/users", None),
                ("POST", "/users", {}),
                ("PATCH", f"/users/{target_id}/role", {}),
            )

            for method, path, body in requests:
                with self.subTest(role=role, method=method):
                    response = self.client.open(
                        path,
                        method=method,
                        headers=headers,
                        **({"json": body} if body is not None else {}),
                    )
                    self.assertEqual(response.status_code, 403)

    def test_07_admin_invalid_payload(self):
        # Body rỗng không được phép tạo hoặc sửa tài khoản.
        response = self.client.post(
            "/users",
            headers=self.admin_headers,
            json={},
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.patch(
            "/users/00000000-0000-0000-0000-000000000001/role",
            headers=self.admin_headers,
            json={},
        )
        self.assertEqual(response.status_code, 400)

    def test_08_wrong_password(self):
        response = self.client.post(
            "/auth/login",
            json={
                "email": "admin@arimms.local",
                "password": self.password + "-intentionally-wrong",
            },
        )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main(verbosity=2)