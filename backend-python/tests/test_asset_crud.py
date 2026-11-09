import getpass
import os
import unittest
from pathlib import Path
from uuid import uuid4

from dotenv import dotenv_values
from sqlalchemy.engine import make_url

from src.create_app import create_app


class TestAssetCRUD(unittest.TestCase):
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

        password = getpass.getpass(
            "Mật khẩu Administrator của database kiểm tra: "
        )

        response = cls.client.post(
            "/auth/login",
            json={
                "email": "admin@arimms.local",
                "password": password,
            },
        )

        if response.status_code != 200:
            raise RuntimeError("Đăng nhập Administrator thất bại.")

        data = response.get_json()

        if data.get("role") != "Administrator":
            raise RuntimeError("Cần tài khoản Administrator.")

        cls.headers = {
            "Authorization": f"Bearer {data['accessToken']}"
        }

    def setUp(self):
        self.prefix = f"AUTO-{uuid4().hex[:12]}"
        self.created = []
        self.addCleanup(self.cleanup_assets)

    def create_asset(self, resource, payload):
        response = self.client.post(
            f"/{resource}",
            headers=self.headers,
            json=payload,
        )
        self.assertEqual(
            response.status_code,
            201,
            response.get_data(as_text=True),
        )

        data = response.get_json()

        self.created.append(
            (resource, data["id"], payload["code"])
        )
        self.assertEqual(data["code"], payload["code"])
        return data

    def cleanup_assets(self):
        errors = []

        # Xóa từ Server lên Site.
        for resource, asset_id, expected_code in reversed(self.created):
            path = f"/{resource}/{asset_id}"
            detail = self.client.get(path, headers=self.headers)

            if detail.status_code == 404:
                continue

            if (
                detail.status_code != 200
                or detail.get_json().get("code") != expected_code
                or not expected_code.startswith(self.prefix)
            ):
                errors.append(f"Không xác nhận được tài sản: {path}")
                continue

            response = self.client.delete(path, headers=self.headers)

            if response.status_code != 200:
                errors.append(
                    f"Xóa thất bại {path}: {response.status_code}"
                )
                continue

            after = self.client.get(path, headers=self.headers)

            if after.status_code != 404:
                errors.append(f"Tài sản vẫn tồn tại: {path}")

        if errors:
            raise AssertionError("; ".join(errors))

    def test_asset_lifecycle(self):
        site = self.create_asset("sites", {
            "code": f"{self.prefix}-SITE",
            "name": "Automated test site",
        })

        room = self.create_asset("rooms", {
            "siteId": site["id"],
            "code": f"{self.prefix}-ROOM",
            "name": "Automated test room",
        })

        rack = self.create_asset("racks", {
            "roomId": room["id"],
            "code": f"{self.prefix}-RACK",
            "name": "Automated test rack",
            "capacityU": 42,
        })

        server = self.create_asset("servers", {
            "rackId": rack["id"],
            "code": f"{self.prefix}-SERVER",
            "name": "Automated test server",
        })

        # Kiểm tra cập nhật và đọc lại cả bốn loại tài sản.
        for resource, asset in (
            ("sites", site),
            ("rooms", room),
            ("racks", rack),
            ("servers", server),
        ):
            with self.subTest(action="update", resource=resource):
                path = f"/{resource}/{asset['id']}"
                new_name = f"Updated {resource}"

                response = self.client.patch(
                    path,
                    headers=self.headers,
                    json={"name": new_name},
                )
                self.assertEqual(response.status_code, 200)

                detail = self.client.get(path, headers=self.headers)
                self.assertEqual(detail.status_code, 200)
                self.assertEqual(
                    detail.get_json()["name"],
                    new_name,
                )

        # Server phải trả đúng toàn bộ cây quan hệ.
        detail = self.client.get(
            f"/servers/{server['id']}",
            headers=self.headers,
        ).get_json()

        self.assertEqual(detail["rack"]["id"], rack["id"])
        self.assertEqual(
            detail["rack"]["room"]["id"], room["id"]
        )
        self.assertEqual(
            detail["rack"]["room"]["site"]["id"], site["id"]
        )

        # Không được xóa tài sản cha đang có dữ liệu con.
        for resource, asset in (
            ("sites", site),
            ("rooms", room),
            ("racks", rack),
        ):
            with self.subTest(action="blocked_delete", resource=resource):
                response = self.client.delete(
                    f"/{resource}/{asset['id']}",
                    headers=self.headers,
                )
                self.assertEqual(response.status_code, 409)

        # Đổi sang Rack không tồn tại phải bị từ chối.
        response = self.client.patch(
            f"/servers/{server['id']}",
            headers=self.headers,
            json={"rackId": str(uuid4())},
        )
        self.assertEqual(response.status_code, 400)

        # Cập nhật trùng mã Server phải bị từ chối.
        response = self.client.patch(
            f"/servers/{server['id']}",
            headers=self.headers,
            json={"code": "DEMO-NODE-01"},
        )
        self.assertEqual(response.status_code, 409)

        # Hai yêu cầu lỗi không được thay đổi dữ liệu Server.
        response = self.client.get(
            f"/servers/{server['id']}",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)

        unchanged = response.get_json()
        self.assertEqual(unchanged["rackId"], rack["id"])
        self.assertEqual(unchanged["code"], server["code"])


if __name__ == "__main__":
    unittest.main(verbosity=2)