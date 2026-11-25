import unittest
from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

from flask import Flask
from sqlalchemy.exc import SQLAlchemyError

from src.api.controllers.audit_controller import create_audit_blueprint
from src.domain.constants import Role


class AuditControllerTests(unittest.TestCase):
    def setUp(self):
        self.auth = Mock()
        self.auth.authenticate_token.side_effect = lambda token: SimpleNamespace(
            role={"admin": Role.ADMINISTRATOR, "tech": Role.TECHNICIAN, "op": Role.OPERATOR}[token]
        )
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        row = SimpleNamespace(id="1", ticket_id="t1", actor_id="u1", action="START", from_status="ASSIGNED", to_status="IN_PROGRESS", created_at=now, note="secret", details={"token": "secret"})
        self.db = Mock()
        self.db.scalars.side_effect = [Mock(all=Mock(return_value=[row])), Mock(all=Mock(return_value=[]))]

        @contextmanager
        def session():
            yield self.db

        app = Flask(__name__)
        app.register_blueprint(create_audit_blueprint(self.auth, session))
        self.client = app.test_client()

    def test_admin_receives_only_whitelisted_fields(self):
        response = self.client.get('/audit', headers={'Authorization': 'Bearer admin'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['items'][0]['object_id'], 't1')
        self.assertNotIn('secret', response.get_data(as_text=True))

    def test_unauthorized_and_other_roles_are_denied(self):
        self.assertEqual(self.client.get('/audit').status_code, 401)
        for role in ('tech', 'op'):
            self.assertEqual(self.client.get('/audit', headers={'Authorization': f'Bearer {role}'}).status_code, 403)
        self.db.scalars.assert_not_called()

    def test_limit_is_validated(self):
        for limit in ('0', '101', 'wrong'):
            self.assertEqual(self.client.get(f'/audit?limit={limit}', headers={'Authorization': 'Bearer admin'}).status_code, 400)
        self.db.scalars.assert_not_called()

    def test_database_error_is_generic(self):
        self.db.scalars.side_effect = SQLAlchemyError('secret database detail')
        response = self.client.get('/audit', headers={'Authorization': 'Bearer admin'})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('secret', response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
