import unittest
from pathlib import Path
from uuid import uuid4

from dotenv import dotenv_values
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError

from src.infrastructure.databases.database import Database


class TestDatabaseConstraints(unittest.TestCase):
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
        self.connection = self.database.engine.connect()
        self.addCleanup(self.connection.close)

        self.transaction = self.connection.begin()
        self.addCleanup(self.transaction.rollback)

    def assert_rejected(self, sql, expected_state, params=None):
        with self.assertRaises(IntegrityError) as caught:
            self.connection.execute(
                text(sql),
                params or {},
            )

        self.assertEqual(
            caught.exception.orig.sqlstate,
            expected_state,
        )

    def test_01_duplicate_email(self):
        """Database phải chặn email trùng."""

        self.assert_rejected(
            """
            UPDATE users
            SET email = 'admin@arimms.local'
            WHERE email = 'operator@arimms.local'
            """,
            "23505",
        )

    def test_02_invalid_rack_capacity(self):
        """Database phải chặn capacity_u bằng 0."""

        self.assert_rejected(
            """
            UPDATE racks
            SET capacity_u = 0
            WHERE code = 'RACK-01'
            """,
            "23514",
        )

    def test_03_missing_parent_site(self):
        """Room không được tham chiếu Site không tồn tại."""

        self.assert_rejected(
            """
            UPDATE rooms
            SET site_id = CAST(:site_id AS uuid)
            WHERE code = 'ROOM-01'
            """,
            "23503",
            {"site_id": str(uuid4())},
        )

    def test_04_delete_site_with_room(self):
        """Không được xóa Site đang có Room."""

        self.assert_rejected(
            """
            DELETE FROM sites
            WHERE code = 'DEMO-SITE'
            """,
            "23503",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)