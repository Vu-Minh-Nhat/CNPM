from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.constants import Role, TicketStatus
from src.domain.exceptions import (
    ForbiddenError,
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)
from src.domain.models.ticket import Ticket
from src.domain.models.ticket_history import TicketHistory
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.alert_repository import AlertRepository
from src.domain.repositories.ticket_history_repository import (
    TicketHistoryRepository,
)
from src.domain.repositories.ticket_repository import TicketRepository


class TicketService:
    MAX_TEXT_LENGTH = 4000

    def __init__(
        self,
        *,
        tickets: TicketRepository,
        history: TicketHistoryRepository,
        accounts: AccountRepository,
        alerts: AlertRepository,
    ):
        self._tickets = tickets
        self._history_repository = history
        self._accounts = accounts
        self._alerts = alerts

    @staticmethod
    def _require_role(role: Role, allowed_roles: tuple[Role, ...]) -> None:
        if role not in allowed_roles:
            raise ForbiddenError(
                "Bạn không có quyền thực hiện thao tác này."
            )

    @classmethod
    def _text(
        cls,
        value,
        field: str,
        *,
        required: bool = False,
    ) -> str | None:
        if value is None and not required:
            return None

        if not isinstance(value, str):
            raise ValidationError(f"{field} phải là chuỗi.")

        value = value.strip()
        if required and not value:
            raise ValidationError(f"{field} không được để trống.")
        if len(value) > cls.MAX_TEXT_LENGTH:
            raise ValidationError(
                f"{field} không được vượt quá "
                f"{cls.MAX_TEXT_LENGTH} ký tự."
            )
        return value

    @staticmethod
    def _version(value) -> int:
        if type(value) is not int or value < 1:
            raise ValidationError(
                "version phải là số nguyên dương."
            )
        return value

    @staticmethod
    def _check_fields(
        data,
        allowed: set[str],
        required: set[str] | None = None,
    ):
        if not isinstance(data, dict):
            raise ValidationError("Dữ liệu phải là object JSON.")

        unknown = set(data) - allowed
        if unknown:
            raise ValidationError(
                "Dữ liệu chứa trường không được hỗ trợ: "
                + ", ".join(sorted(unknown))
            )

        missing = (required or set()) - set(data)
        if missing:
            raise ValidationError(
                "Thiếu trường bắt buộc: "
                + ", ".join(sorted(missing))
            )

    @staticmethod
    def _uuid(value, field: str) -> str:
        if not isinstance(value, str):
            raise ValidationError(f"{field} phải là UUID hợp lệ.")
        try:
            return str(UUID(value))
        except ValueError as error:
            raise ValidationError(f"{field} phải là UUID hợp lệ.") from error

    @staticmethod
    def _history(
        *,
        ticket_id: str,
        actor_id: str,
        action: str,
        from_status: str | None,
        to_status: str | None,
        note: str | None = None,
        details: dict | None = None,
        created_at: datetime,
    ) -> TicketHistory:
        return TicketHistory(
            id=str(uuid4()),
            ticket_id=ticket_id,
            actor_id=actor_id,
            action=action,
            from_status=from_status,
            to_status=to_status,
            note=note,
            created_at=created_at,
            details=details,
        )

    def create_ticket(self, actor_id: str, data: dict) -> dict:
        self._check_fields(
            data,
            {"node_id", "alert_id", "title", "description"},
            {"node_id", "title", "description"},
        )
        node_id = self._uuid(data["node_id"], "node_id")
        alert_id = data.get("alert_id")
        if alert_id is not None:
            alert_id = self._uuid(alert_id, "alert_id")
            alert = self._alerts.find_by_id(alert_id)
            if alert is None:
                raise ResourceNotFoundError("Không tìm thấy cảnh báo.")
            if self._uuid(alert.node_id, "alert.node_id") != node_id:
                raise ValidationError(
                    "Node của ticket phải trùng với Node của cảnh báo."
                )

        title = self._text(data["title"], "title", required=True)
        description = self._text(
            data["description"],
            "description",
            required=True,
        )
        if len(title) > 200:
            raise ValidationError("title không được vượt quá 200 ký tự.")

        now = datetime.now(timezone.utc)
        ticket = Ticket(
            id=str(uuid4()),
            node_id=node_id,
            alert_id=alert_id,
            created_by=actor_id,
            assigned_to=None,
            status=TicketStatus.NEW.value,
            title=title,
            description=description,
            created_at=now,
            updated_at=now,
        )
        history = self._history(
            ticket_id=ticket.id,
            actor_id=actor_id,
            action="CREATE",
            from_status=None,
            to_status=TicketStatus.NEW.value,
            details={
                "node_id": node_id,
                "alert_id": alert_id,
                "title": title,
                "description": description,
            },
            created_at=now,
        )
        created = self._tickets.create_with_history(ticket, history)
        return self._ticket_response(created)

    def list_tickets(
        self,
        *,
        role: Role,
        actor_id: str,
        status: str | None = None,
    ) -> list[dict]:
        self._require_role(role, (Role.OPERATOR, Role.TECHNICIAN))
        self._validate_status(status)

        tickets = (
            self._tickets.list_all(status)
            if role == Role.OPERATOR
            else self._tickets.list_by_assignee(actor_id, status)
        )
        return [self._ticket_response(ticket) for ticket in tickets]

    def list_active_technicians(self, role: Role) -> list[dict]:
        self._require_role(role, (Role.OPERATOR,))
        return [
            {"id": account.id, "email": account.email}
            for account in self._accounts.list_accounts()
            if account.role == Role.TECHNICIAN and account.is_active
        ]

    def get_ticket(
        self,
        ticket_id: str,
        *,
        role: Role,
        actor_id: str,
    ) -> dict:
        ticket = self._get_accessible_ticket(
            ticket_id,
            role=role,
            actor_id=actor_id,
        )
        result = self._ticket_response(ticket)
        result["history"] = [
            self._history_response(item)
            for item in self._history_repository.list_by_ticket(ticket.id)
        ]
        return result

    def assign_ticket(
        self,
        ticket_id: str,
        actor_id: str,
        data: dict,
    ) -> dict:
        self._check_fields(
            data,
            {"assigned_to", "version", "note"},
            {"assigned_to", "version"},
        )
        assigned_to = self._uuid(data["assigned_to"], "assigned_to")
        version = self._version(data["version"])
        note = self._text(data.get("note"), "note")

        technician = self._accounts.find_by_id(assigned_to)
        if (
            technician is None
            or technician.role != Role.TECHNICIAN
            or not technician.is_active
        ):
            raise ValidationError(
                "Chỉ được phân công cho Technician đang hoạt động."
            )

        ticket = self._tickets.find_by_id(ticket_id)
        if ticket is None:
            raise ResourceNotFoundError("Không tìm thấy ticket.")
        if ticket.status not in (
            TicketStatus.NEW.value,
            TicketStatus.ASSIGNED.value,
        ):
            raise ResourceConflictError(
                "Chỉ ticket mới hoặc đã phân công mới được phân công lại."
            )

        now = datetime.now(timezone.utc)
        history = self._history(
            ticket_id=ticket.id,
            actor_id=actor_id,
            action="ASSIGN",
            from_status=ticket.status,
            to_status=TicketStatus.ASSIGNED.value,
            note=note,
            details={
                "assigned_to": {
                    "from": ticket.assigned_to,
                    "to": assigned_to,
                }
            },
            created_at=now,
        )
        updated = self._tickets.update_with_history(
            ticket_id,
            version,
            {
                "assigned_to": assigned_to,
                "status": TicketStatus.ASSIGNED.value,
            },
            history,
        )
        if updated is None:
            raise ResourceNotFoundError("Không tìm thấy ticket.")
        return self._ticket_response(updated)

    def start_ticket(
        self,
        ticket_id: str,
        actor_id: str,
        data: dict,
    ) -> dict:
        self._check_fields(data, {"version", "note"}, {"version"})
        version = self._version(data["version"])
        note = self._text(data.get("note"), "note")
        ticket = self._get_accessible_ticket(
            ticket_id,
            role=Role.TECHNICIAN,
            actor_id=actor_id,
        )
        self._expect_status(ticket, TicketStatus.ASSIGNED)
        return self._transition(
            ticket,
            actor_id=actor_id,
            version=version,
            action="START",
            to_status=TicketStatus.IN_PROGRESS,
            note=note,
        )

    def update_work(
        self,
        ticket_id: str,
        actor_id: str,
        data: dict,
    ) -> dict:
        allowed = {"version", "progress", "work_notes", "evidence"}
        self._check_fields(data, allowed)
        if "version" not in data:
            raise ValidationError("Thiếu trường bắt buộc: version.")
        changes = {}
        for field in ("progress", "work_notes", "evidence"):
            if field not in data:
                continue
            value = data[field]
            if field == "progress":
                if type(value) is not int or not 0 <= value <= 100:
                    raise ValidationError(
                        "progress phải là số nguyên từ 0 đến 100."
                    )
                changes[field] = value
            else:
                changes[field] = self._text(value, field)
        if not changes:
            raise ValidationError(
                "Cần cập nhật ít nhất một trường công việc."
            )
        version = self._version(data["version"])
        ticket = self._get_accessible_ticket(
            ticket_id,
            role=Role.TECHNICIAN,
            actor_id=actor_id,
        )
        self._expect_status(ticket, TicketStatus.IN_PROGRESS)
        event_details = {
            "changes": {
                field: {
                    "from": getattr(ticket, field),
                    "to": value,
                }
                for field, value in changes.items()
            }
        }
        now = datetime.now(timezone.utc)
        history = self._history(
            ticket_id=ticket.id,
            actor_id=actor_id,
            action="UPDATE_WORK",
            from_status=ticket.status,
            to_status=ticket.status,
            note=None,
            details=event_details,
            created_at=now,
        )
        updated = self._tickets.update_with_history(
            ticket.id,
            version,
            changes,
            history,
        )
        if updated is None:
            raise ResourceNotFoundError("Không tìm thấy ticket.")
        return self._ticket_response(updated)

    def submit_for_approval(
        self,
        ticket_id: str,
        actor_id: str,
        data: dict,
    ) -> dict:
        self._check_fields(
            data,
            {"version", "result", "evidence", "note"},
            {"version", "result"},
        )
        version = self._version(data["version"])
        result = self._text(data["result"], "result", required=True)
        evidence = (
            self._text(data["evidence"], "evidence")
            if "evidence" in data
            else None
        )
        note = self._text(data.get("note"), "note")
        ticket = self._get_accessible_ticket(
            ticket_id,
            role=Role.TECHNICIAN,
            actor_id=actor_id,
        )
        self._expect_status(ticket, TicketStatus.IN_PROGRESS)

        changes = {
            "status": TicketStatus.PENDING_APPROVAL.value,
            "progress": 100,
            "result": result,
        }
        if evidence is not None:
            changes["evidence"] = evidence
        now = datetime.now(timezone.utc)
        history = self._history(
            ticket_id=ticket.id,
            actor_id=actor_id,
            action="SUBMIT_FOR_APPROVAL",
            from_status=ticket.status,
            to_status=TicketStatus.PENDING_APPROVAL.value,
            note=note,
            details={
                "result": result,
                "evidence": evidence if evidence is not None else ticket.evidence,
            },
            created_at=now,
        )
        updated = self._tickets.update_with_history(
            ticket.id,
            version,
            changes,
            history,
        )
        if updated is None:
            raise ResourceNotFoundError("Không tìm thấy ticket.")
        return self._ticket_response(updated)

    def approve_close(
        self,
        ticket_id: str,
        actor_id: str,
        data: dict,
    ) -> dict:
        self._check_fields(data, {"version", "note"}, {"version"})
        version = self._version(data["version"])
        note = self._text(data.get("note"), "note")
        ticket = self._tickets.find_by_id(ticket_id)
        if ticket is None:
            raise ResourceNotFoundError("Không tìm thấy ticket.")
        self._expect_status(ticket, TicketStatus.PENDING_APPROVAL)
        if not ticket.result or not ticket.result.strip():
            raise ResourceConflictError(
                "Không thể đóng ticket khi thiếu kết quả xử lý."
            )
        return self._transition(
            ticket,
            actor_id=actor_id,
            version=version,
            action="APPROVE_CLOSE",
            to_status=TicketStatus.CLOSED,
            note=note,
        )

    def return_for_work(
        self,
        ticket_id: str,
        actor_id: str,
        data: dict,
    ) -> dict:
        self._check_fields(
            data,
            {"version", "reason"},
            {"version", "reason"},
        )
        version = self._version(data["version"])
        reason = self._text(data["reason"], "reason", required=True)
        ticket = self._tickets.find_by_id(ticket_id)
        if ticket is None:
            raise ResourceNotFoundError("Không tìm thấy ticket.")
        self._expect_status(ticket, TicketStatus.PENDING_APPROVAL)
        now = datetime.now(timezone.utc)
        history = self._history(
            ticket_id=ticket.id,
            actor_id=actor_id,
            action="RETURN_FOR_WORK",
            from_status=ticket.status,
            to_status=TicketStatus.IN_PROGRESS.value,
            note=reason,
            details={"previous_result": ticket.result},
            created_at=now,
        )
        updated = self._tickets.update_with_history(
            ticket.id,
            version,
            {
                "status": TicketStatus.IN_PROGRESS.value,
                "result": None,
            },
            history,
        )
        if updated is None:
            raise ResourceNotFoundError("Không tìm thấy ticket.")
        return self._ticket_response(updated)

    def _transition(
        self,
        ticket: Ticket,
        *,
        actor_id: str,
        version: int,
        action: str,
        to_status: TicketStatus,
        note: str | None,
    ) -> dict:
        now = datetime.now(timezone.utc)
        history = self._history(
            ticket_id=ticket.id,
            actor_id=actor_id,
            action=action,
            from_status=ticket.status,
            to_status=to_status.value,
            note=note,
            created_at=now,
        )
        updated = self._tickets.update_with_history(
            ticket.id,
            version,
            {"status": to_status.value},
            history,
        )
        if updated is None:
            raise ResourceNotFoundError("Không tìm thấy ticket.")
        return self._ticket_response(updated)

    def _get_accessible_ticket(
        self,
        ticket_id: str,
        *,
        role: Role,
        actor_id: str,
    ) -> Ticket:
        self._require_role(role, (Role.OPERATOR, Role.TECHNICIAN))
        ticket = self._tickets.find_by_id(ticket_id)
        if ticket is None:
            raise ResourceNotFoundError("Không tìm thấy ticket.")
        if role == Role.TECHNICIAN and ticket.assigned_to != actor_id:
            raise ForbiddenError(
                "Bạn chỉ được truy cập ticket được phân công."
            )
        return ticket

    @staticmethod
    def _expect_status(ticket: Ticket, expected: TicketStatus) -> None:
        if ticket.status != expected.value:
            raise ResourceConflictError(
                f"Ticket phải ở trạng thái {expected.value}."
            )

    @staticmethod
    def _validate_status(status: str | None) -> None:
        if status is not None and status not in {
            item.value for item in TicketStatus
        }:
            raise ValidationError("Trạng thái ticket không hợp lệ.")

    @staticmethod
    def _ticket_response(ticket: Ticket) -> dict:
        return {
            "id": ticket.id,
            "node_id": ticket.node_id,
            "alert_id": ticket.alert_id,
            "created_by": ticket.created_by,
            "assigned_to": ticket.assigned_to,
            "status": ticket.status,
            "title": ticket.title,
            "description": ticket.description,
            "progress": ticket.progress,
            "work_notes": ticket.work_notes,
            "evidence": ticket.evidence,
            "result": ticket.result,
            "version": ticket.version,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat(),
        }

    def _history_response(self, history: TicketHistory) -> dict:
        actor = self._accounts.find_by_id(history.actor_id)
        return {
            "id": history.id,
            "ticket_id": history.ticket_id,
            "actor_id": history.actor_id,
         "actor_email": actor.email if actor is not None else None,
            "action": history.action,
            "from_status": history.from_status,
            "to_status": history.to_status,
            "note": history.note,
            "details": history.details,
            "created_at": history.created_at.isoformat(),
        }
