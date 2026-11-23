import unittest
from unittest.mock import Mock
from uuid import uuid4

from src.domain.constants import Role
from src.domain.exceptions import AuthenticationError
from src.domain.models.account import Account
from src.services.session_service import SessionService


class TestSessionRoleIsLoadedFromDatabase(unittest.TestCase):
    def setUp(self):
        self.account_id = str(uuid4())
        self.accounts = Mock()
        self.tokens = Mock()
        self.tokens.verify.return_value = self.account_id
        self.service = SessionService(self.accounts, self.tokens)

    def _account(self, role: Role, is_active: bool = True) -> Account:
        return Account(
            id=self.account_id,
            email="user@arimms.local",
            role=role,
            is_active=is_active,
            password_hash="not-used-in-this-test",
        )

    def test_role_is_taken_from_current_database_record(self):
        # Token cũ có thể từng được phát khi tài khoản là Administrator.
        # SessionService phải dùng role mới đọc từ repository/database.
        self.accounts.find_by_id.return_value = self._account(Role.TECHNICIAN)

        account = self.service.authenticate_token("old-admin-token")

        self.tokens.verify.assert_called_once_with("old-admin-token")
        self.accounts.find_by_id.assert_called_once_with(self.account_id)
        self.assertEqual(account.role, Role.TECHNICIAN)

    def test_disabled_account_is_rejected(self):
        self.accounts.find_by_id.return_value = self._account(
            Role.ADMINISTRATOR,
            is_active=False,
        )

        with self.assertRaises(AuthenticationError):
            self.service.authenticate_token("valid-token")

    def test_missing_account_is_rejected(self):
        self.accounts.find_by_id.return_value = None

        with self.assertRaises(AuthenticationError):
            self.service.authenticate_token("valid-token")


if __name__ == "__main__":
    unittest.main(verbosity=2)
