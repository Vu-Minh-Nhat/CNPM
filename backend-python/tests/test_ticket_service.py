import unittest
from dataclasses import replace
from datetime import datetime, timezone
from flask import Flask
from unittest.mock import MagicMock
from uuid import uuid4

from src.domain.constants import Role
from src.domain.exceptions import (
    ForbiddenError,
    ResourceConflictError,
    ValidationError,
)
from src.domain.models.account import Account
from src.domain.models.alert import Alert
from src.domain.models.ticket import Ticket
from src.api.controllers.tickets_controller import (
    create_tickets_blueprint,
)
from src.api.error_handlers import register_error_handlers
from src.services.ticket_service import TicketService


class InMemoryTickets:
    def __init__(self):
        self.items = {}
        self.committed_history = []

    def create_with_history(self, ticket, history):
        self.items[ticket.id] = ticket
        self.committed_history.append(history)
        return ticket

    def update_with_history(
        self,
        ticket_id,
        expected_version,
        changes,
        history,
    ):
        ticket = self.items.get(ticket_id)
        if ticket is None:
            return None
        if ticket.version != expected_version:
            raise ResourceConflictError("stale version")
        updated = replace(
            ticket,
            **changes,
            updated_at=datetime.now(timezone.utc),
            version=ticket.version + 1,
        )
        self.items[ticket_id] = updated
        self.committed_history.append(history)
        return updated

    def find_by_id(self, ticket_id):
        return self.items.get(ticket_id)

    def list_all(self, status=None):
        return [
            item for item in self.items.values()
            if status is None or item.status == status
        ]

    def list_by_assignee(self, assigned_to, status=None):
        return [
            item for item in self.items.values()
            if item.assigned_to == assigned_to
            and (status is None or item.status == status)
        ]


class InMemoryHistory:
    def __init__(self, tickets):
        self._tickets = tickets

    def list_by_ticket(self, ticket_id):
        return [
            entry for entry in self._tickets.committed_history
            if entry.ticket_id == ticket_id
        ]


class TestTicketService(unittest.TestCase):
    def setUp(self):
        self.operator_id = str(uuid4())
        self.technician_id = str(uuid4())
        self.other_technician_id = str(uuid4())
        self.node_id = str(uuid4())
        self.alert_id = str(uuid4())

        self.tickets = InMemoryTickets()
        self.accounts = MagicMock()
        self.alerts = MagicMock()
        self.service = TicketService(
            tickets=self.tickets,
            history=InMemoryHistory(self.tickets),
            accounts=self.accounts,
            alerts=self.alerts,
        )
        self.accounts.find_by_id.return_value = Account(
            id=self.technician_id,
            email="tech@example.test",
            role=Role.TECHNICIAN,
            is_active=True,
            password_hash="",
        )

    def create_ticket(self, alert_id=None):
        data = {
            "node_id": self.node_id,
            "title": "Replace failed drive",
            "description": "Inspect and replace the drive.",
        }
        if alert_id is not None:
            data["alert_id"] = alert_id
        return self.service.create_ticket(self.operator_id, data)

    def assign_and_start(self, ticket):
        ticket = self.service.assign_ticket(
            ticket["id"],
            self.operator_id,
            {
                "assigned_to": self.technician_id,
                "version": ticket["version"],
            },
        )
        ticket = self.service.start_ticket(
            ticket["id"],
            self.technician_id,
            {"version": ticket["version"]},
        )
        return ticket

    def test_create_assign_work_submit_and_approve(self):
        ticket = self.assign_and_start(self.create_ticket())
        ticket = self.service.update_work(
            ticket["id"],
            self.technician_id,
            {
                "version": ticket["version"],
                "progress": 65,
                "work_notes": "Drive replaced; running diagnostics.",
                "evidence": "https://evidence.example.test/drive-check",
            },
        )
        ticket = self.service.submit_for_approval(
            ticket["id"],
            self.technician_id,
            {
                "version": ticket["version"],
                "result": "Diagnostics passed.",
            },
        )
        self.assertEqual(ticket["status"], "PENDING_APPROVAL")
        self.assertEqual(ticket["progress"], 100)

        ticket = self.service.approve_close(
            ticket["id"],
            self.operator_id,
            {"version": ticket["version"], "note": "Verified."},
        )

        self.assertEqual(ticket["status"], "CLOSED")
        self.assertEqual(
            [item.action for item in self.tickets.committed_history],
            [
                "CREATE",
                "ASSIGN",
                "START",
                "UPDATE_WORK",
                "SUBMIT_FOR_APPROVAL",
                "APPROVE_CLOSE",
            ],
        )
        self.assertTrue(all(
            item.actor_id
            and item.created_at.tzinfo is not None
            for item in self.tickets.committed_history
        ))
        self.assertEqual(
            self.tickets.committed_history[3].details["changes"]["progress"],
            {"from": 0, "to": 65},
        )
        self.alerts.recover.assert_not_called()

    def test_create_ticket_from_matching_alert(self):
        self.alerts.find_by_id.return_value = Alert(
            id=self.alert_id,
            node_id=self.node_id,
            rule_id=None,
            metric="cpu_percent",
            operator=">=",
            threshold=80,
            severity="HIGH",
            status="FIRING",
            message="CPU high",
            triggered_at=datetime.now(timezone.utc),
            acknowledged_at=None,
            recovered_at=None,
        )

        ticket = self.create_ticket(self.alert_id)

        self.assertEqual(ticket["alert_id"], self.alert_id)
        self.assertEqual(ticket["node_id"], self.node_id)

    def test_operator_can_return_ticket_with_reason(self):
        ticket = self.assign_and_start(self.create_ticket())
        ticket = self.service.submit_for_approval(
            ticket["id"],
            self.technician_id,
            {
                "version": ticket["version"],
                "result": "Initial diagnostics passed.",
            },
        )

        returned = self.service.return_for_work(
            ticket["id"],
            self.operator_id,
            {
                "version": ticket["version"],
                "reason": "Attach a post-repair health check.",
            },
        )

        self.assertEqual(returned["status"], "IN_PROGRESS")
        self.assertIsNone(returned["result"])
        self.assertEqual(
            self.tickets.committed_history[-1].note,
            "Attach a post-repair health check.",
        )

    def test_assignment_requires_active_technician(self):
        ticket = self.create_ticket()
        self.accounts.find_by_id.return_value = Account(
            id=self.other_technician_id,
            email="operator@example.test",
            role=Role.OPERATOR,
            is_active=True,
            password_hash="",
        )

        with self.assertRaises(ValidationError):
            self.service.assign_ticket(
                ticket["id"],
                self.operator_id,
                {
                    "assigned_to": self.other_technician_id,
                    "version": ticket["version"],
                },
            )

        self.assertEqual(ticket["status"], "NEW")
        self.assertEqual(len(self.tickets.committed_history), 1)

        self.accounts.find_by_id.return_value = Account(
            id=self.technician_id,
            email="tech@example.test",
            role=Role.TECHNICIAN,
            is_active=False,
            password_hash="",
        )
        with self.assertRaises(ValidationError):
            self.service.assign_ticket(
                ticket["id"],
                self.operator_id,
                {
                    "assigned_to": self.technician_id,
                    "version": ticket["version"],
                },
            )

    def test_technician_cannot_access_an_unassigned_ticket(self):
        ticket = self.create_ticket()
        with self.assertRaises(ForbiddenError):
            self.service.get_ticket(
                ticket["id"],
                role=Role.TECHNICIAN,
                actor_id=self.technician_id,
            )

    def test_alert_must_belong_to_same_node(self):
        self.alerts.find_by_id.return_value = Alert(
            id=self.alert_id,
            node_id=str(uuid4()),
            rule_id=None,
            metric="cpu_percent",
            operator=">=",
            threshold=80,
            severity="HIGH",
            status="FIRING",
            message="CPU high",
            triggered_at=datetime.now(timezone.utc),
            acknowledged_at=None,
            recovered_at=None,
        )

        with self.assertRaises(ValidationError):
            self.create_ticket(self.alert_id)
        self.assertFalse(self.tickets.items)
        self.assertFalse(self.tickets.committed_history)

    def test_invalid_transitions_result_and_stale_version_are_rejected(self):
        ticket = self.create_ticket()
        assigned = self.service.assign_ticket(
            ticket["id"],
            self.operator_id,
            {
                "assigned_to": self.technician_id,
                "version": ticket["version"],
            },
        )
        started = self.service.start_ticket(
            ticket["id"],
            self.technician_id,
            {"version": assigned["version"]},
        )
        with self.assertRaises(ResourceConflictError):
            self.service.start_ticket(
                ticket["id"],
                self.technician_id,
                {"version": started["version"]},
            )
        with self.assertRaises(ValidationError):
            self.service.submit_for_approval(
                ticket["id"],
                self.technician_id,
                {"version": started["version"], "result": "  "},
            )
        with self.assertRaises(ResourceConflictError):
            self.service.update_work(
                ticket["id"],
                self.technician_id,
                {"version": assigned["version"], "progress": 50},
            )

    def test_technician_ticket_list_is_limited_to_assignments(self):
        ticket = self.create_ticket()
        other = self.create_ticket()
        self.service.assign_ticket(
            ticket["id"],
            self.operator_id,
            {
                "assigned_to": self.technician_id,
                "version": ticket["version"],
            },
        )
        self.service.assign_ticket(
            other["id"],
            self.operator_id,
            {
                "assigned_to": self.other_technician_id,
                "version": other["version"],
            },
        )

        results = self.service.list_tickets(
            role=Role.TECHNICIAN,
            actor_id=self.technician_id,
        )

        self.assertEqual([item["id"] for item in results], [ticket["id"]])

    def test_api_enforces_operator_and_assigned_technician_access(self):
        accounts_by_token = {
            "operator": Account(
                id=self.operator_id,
                email="operator@example.test",
                role=Role.OPERATOR,
                is_active=True,
                password_hash="",
            ),
            "technician": Account(
                id=self.technician_id,
                email="tech@example.test",
                role=Role.TECHNICIAN,
                is_active=True,
                password_hash="",
            ),
        }
        session_service = MagicMock()
        session_service.authenticate_token.side_effect = (
            accounts_by_token.__getitem__
        )
        app = Flask(__name__)
        register_error_handlers(app)
        app.register_blueprint(
            create_tickets_blueprint(
                ticket_service=self.service,
                session_service=session_service,
            )
        )
        client = app.test_client()

        unauthenticated = client.get("/tickets")
        self.assertEqual(unauthenticated.status_code, 401)

        forbidden_create = client.post(
            "/tickets",
            headers={"Authorization": "Bearer technician"},
            json={},
        )
        self.assertEqual(forbidden_create.status_code, 403)

        created = client.post(
            "/tickets",
            headers={"Authorization": "Bearer operator"},
            json={
                "node_id": self.node_id,
                "title": "Maintenance",
                "description": "Check the Node.",
            },
        )
        self.assertEqual(created.status_code, 201)

        forbidden_detail = client.get(
            f"/tickets/{created.get_json()['id']}",
            headers={"Authorization": "Bearer technician"},
        )
        self.assertEqual(forbidden_detail.status_code, 403)


if __name__ == "__main__":
    unittest.main(verbosity=2)
