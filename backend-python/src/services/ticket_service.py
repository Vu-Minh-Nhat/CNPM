from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


ALLOWED_EVIDENCE_MIMES = {
    "image/png",
    "image/jpeg",
    "application/pdf",
    "text/plain",
    "application/json",
}
MAX_EVIDENCE_BYTES = 10 * 1024 * 1024  # 10 MB

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "OPEN": {"ASSIGNED"},
    "ASSIGNED": {"IN_PROGRESS", "ASSIGNED"},
    "IN_PROGRESS": {"PENDING_REVIEW", "ASSIGNED"},
    "PENDING_REVIEW": {"CLOSED", "IN_PROGRESS"},
    "CLOSED": set(),
}


class TicketError(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "BAD_REQUEST") -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


@dataclass
class Actor:
    user_id: str
    role: str  # ADMIN | OPERATOR | TECHNICIAN | VIEWER
    allowed_node_ids: set[str] = field(default_factory=set)


class TicketService:
    """Service quản lý vòng đời ticket bảo trì, độc lập với trạng thái cảnh báo."""

    def __init__(self, repo: Any, audit_logger: Any) -> None:
        self.repo = repo
        self.audit = audit_logger

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _check_read_scope(self, actor: Actor, ticket: dict[str, Any]) -> None:
        if actor.role in {"ADMIN", "OPERATOR", "VIEWER"}:
            if actor.allowed_node_ids and ticket["node_id"] not in actor.allowed_node_ids:
                raise TicketError("Không có quyền truy cập ticket ngoài phạm vi", 403, "FORBIDDEN_SCOPE")
            return
        if actor.role == "TECHNICIAN":
            if ticket.get("assignee_id") != actor.user_id:
                raise TicketError("Technician chỉ được xem ticket được giao cho mình", 403, "FORBIDDEN_TICKET")
            if actor.allowed_node_ids and ticket["node_id"] not in actor.allowed_node_ids:
                raise TicketError("Ticket nằm ngoài phạm vi Node được phân quyền", 403, "FORBIDDEN_SCOPE")
            return
        raise TicketError("Vai trò không hợp lệ", 403, "FORBIDDEN")

    def _check_tech_write_scope(self, actor: Actor, ticket: dict[str, Any]) -> None:
        if actor.role == "ADMIN":
            return
        if actor.role != "TECHNICIAN":
            raise TicketError("Chỉ Technician được giao mới có quyền cập nhật xử lý", 403, "FORBIDDEN")
        if ticket.get("assignee_id") != actor.user_id:
            raise TicketError("Không được cập nhật ticket không được giao cho bạn", 403, "FORBIDDEN_TICKET")
        if actor.allowed_node_ids and ticket["node_id"] not in actor.allowed_node_ids:
            raise TicketError("Ticket ngoài phạm vi Node được phép xử lý", 403, "FORBIDDEN_SCOPE")

    def _check_operator_or_admin(self, actor: Actor, action_label: str) -> None:
        if actor.role not in {"ADMIN", "OPERATOR"}:
            raise TicketError(f"Vai trò {actor.role} không có quyền {action_label}", 403, "FORBIDDEN")

    def _validate_technician(self, technician_id: str) -> dict[str, Any]:
        tech = self.repo.get_user(technician_id)
        if not tech:
            raise TicketError("Không tìm thấy tài khoản Technician", 404, "TECH_NOT_FOUND")
        if tech.get("role") != "TECHNICIAN":
            raise TicketError("Chỉ được phân công cho tài khoản có vai trò TECHNICIAN", 422, "INVALID_ROLE")
        if not tech.get("is_active", False):
            raise TicketError("Tài khoản Technician đã bị khóa hoặc ngừng hoạt động", 422, "INACTIVE_USER")
        return tech

    def _validate_node_and_alert(self, node_id: str, alert_id: str | None) -> dict[str, Any] | None:
        node = self.repo.get_node(node_id)
        if not node:
            raise TicketError(f"Node '{node_id}' không tồn tại", 404, "NODE_NOT_FOUND")

        if not alert_id:
            return None

        alert = self.repo.get_alert(alert_id)
        if not alert:
            raise TicketError(f"Cảnh báo '{alert_id}' không tồn tại", 404, "ALERT_NOT_FOUND")
        if alert.get("node_id") != node_id:
            raise TicketError(
                f"Cảnh báo '{alert_id}' thuộc node '{alert.get('node_id')}', không khớp với node '{node_id}'",
                422,
                "ALERT_NODE_MISMATCH",
            )
        return alert

    def _check_version(self, ticket: dict[str, Any], expected_version: int | None) -> None:
        if expected_version is not None and ticket["version"] != expected_version:
            raise TicketError(
                f"Xung đột cập nhật: phiên bản hiện tại là {ticket['version']}, nhận {expected_version}",
                409,
                "VERSION_CONFLICT",
            )

    def _record_mutation(
        self,
        ticket: dict[str, Any],
        actor: Actor,
        extra_changes: dict[str, Any],
        audit_event: str,
        target_status: str | None = None,
    ) -> dict[str, Any]:
        current_status = ticket["status"]
        next_status = target_status if target_status is not None else current_status
        if next_status != current_status and next_status not in ALLOWED_TRANSITIONS.get(current_status, set()):
            raise TicketError(
                f"Không thể chuyển trạng thái ticket từ {current_status} sang {next_status}",
                422,
                "INVALID_TRANSITION",
            )

        now = self._now()
        changes: dict[str, Any] = {}
        for k, v in extra_changes.items():
            if ticket.get(k) != v:
                changes[k] = {"from": ticket.get(k), "to": v}
                ticket[k] = v

        if next_status != current_status:
            changes["status"] = {"from": current_status, "to": next_status}
            ticket["status"] = next_status

        ticket["version"] += 1
        ticket["updated_at"] = now
        if next_status == "CLOSED":
            ticket["closed_at"] = now

        ticket.setdefault("history", []).append(
            {
                "id": str(uuid4()),
                "ticket_id": ticket["id"],
                "actor_id": actor.user_id,
                "actor_role": actor.role,
                "action": audit_event,
                "from_status": current_status,
                "to_status": ticket["status"],
                "changes": changes,
                "created_at": now,
            }
        )
        self.repo.save_ticket(ticket)
        self.audit.record(
            event=audit_event,
            actor_id=actor.user_id,
            actor_role=actor.role,
            resource_type="maintenance_ticket",
            resource_id=ticket["id"],
            metadata={
                "node_id": ticket["node_id"],
                "alert_id": ticket.get("alert_id"),
                "from_status": current_status,
                "to_status": ticket["status"],
                "version": ticket["version"],
                "changes": changes,
            },
        )
        return ticket

    def create_ticket(self, actor: Actor, payload: dict[str, Any]) -> dict[str, Any]:
        self._check_operator_or_admin(actor, "tạo ticket")
        title = (payload.get("title") or "").strip()
        node_id = (payload.get("node_id") or "").strip()
        alert_id = payload.get("alert_id")
        assignee_id = payload.get("assignee_id")

        if not title or not node_id:
            raise TicketError("Thiếu 'title' hoặc 'node_id'", 400, "MISSING_FIELDS")

        self._validate_node_and_alert(node_id, alert_id)

        initial_status = "OPEN"
        if assignee_id:
            self._validate_technician(assignee_id)
            initial_status = "ASSIGNED"

        now = self._now()
        ticket_id = str(uuid4())
        ticket = {
            "id": ticket_id,
            "code": self.repo.next_ticket_code(),
            "title": title,
            "description": (payload.get("description") or "").strip(),
            "node_id": node_id,
            "alert_id": alert_id,
            "status": initial_status,
            "assignee_id": assignee_id,
            "progress_pct": 0,
            "work_notes": "",
            "result_summary": "",
            "return_reason": None,
            "evidences": [],
            "history": [],
            "version": 1,
            "created_by": actor.user_id,
            "created_at": now,
            "updated_at": now,
            "closed_at": None,
        }
        ticket["history"].append(
            {
                "id": str(uuid4()),
                "ticket_id": ticket_id,
                "actor_id": actor.user_id,
                "actor_role": actor.role,
                "action": "ticket_created",
                "from_status": None,
                "to_status": initial_status,
                "changes": {"node_id": node_id, "alert_id": alert_id, "assignee_id": assignee_id},
                "created_at": now,
            }
        )
        self.repo.save_ticket(ticket)
        self.audit.record(
            event="ticket_created",
            actor_id=actor.user_id,
            actor_role=actor.role,
            resource_type="maintenance_ticket",
            resource_id=ticket_id,
            metadata={"node_id": node_id, "alert_id": alert_id, "status": initial_status},
        )
        return ticket

    def get_ticket(self, actor: Actor, ticket_id: str) -> dict[str, Any]:
        ticket = self.repo.get_ticket(ticket_id)
        if not ticket:
            raise TicketError("Không tìm thấy ticket", 404, "TICKET_NOT_FOUND")
        self._check_read_scope(actor, ticket)
        return ticket

    def list_tickets(self, actor: Actor, filters: dict[str, Any]) -> list[dict[str, Any]]:
        items = self.repo.list_tickets(filters)
        result: list[dict[str, Any]] = []
        for item in items:
            try:
                self._check_read_scope(actor, item)
                result.append(item)
            except TicketError:
                continue
        return result

    def assign_ticket(self, actor: Actor, ticket_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._check_operator_or_admin(actor, "phân công ticket")
        ticket = self.repo.get_ticket(ticket_id)
        if not ticket:
            raise TicketError("Không tìm thấy ticket", 404, "TICKET_NOT_FOUND")
        self._check_version(ticket, payload.get("expected_version"))

        assignee_id = (payload.get("assignee_id") or "").strip()
        if not assignee_id:
            raise TicketError("Thiếu 'assignee_id'", 400, "MISSING_ASSIGNEE")
        self._validate_technician(assignee_id)

        return self._record_mutation(
            ticket=ticket,
            actor=actor,
            extra_changes={"assignee_id": assignee_id, "return_reason": None},
            audit_event="ticket_assigned",
            target_status="ASSIGNED",
        )

    def start_work(self, actor: Actor, ticket_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        ticket = self.repo.get_ticket(ticket_id)
        if not ticket:
            raise TicketError("Không tìm thấy ticket", 404, "TICKET_NOT_FOUND")
        self._check_tech_write_scope(actor, ticket)
        self._check_version(ticket, payload.get("expected_version"))

        return self._record_mutation(
            ticket=ticket,
            actor=actor,
            extra_changes={},
            audit_event="ticket_status_changed",
            target_status="IN_PROGRESS",
        )

    def update_work(self, actor: Actor, ticket_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        ticket = self.repo.get_ticket(ticket_id)
        if not ticket:
            raise TicketError("Không tìm thấy ticket", 404, "TICKET_NOT_FOUND")
        self._check_tech_write_scope(actor, ticket)
        self._check_version(ticket, payload.get("expected_version"))

        if ticket["status"] not in {"ASSIGNED", "IN_PROGRESS"}:
            raise TicketError(
                f"Không thể cập nhật nội dung xử lý khi ticket đang ở trạng thái {ticket['status']}",
                422,
                "INVALID_STATE_FOR_WORK",
            )

        updates: dict[str, Any] = {}
        if "progress_pct" in payload:
            pct = payload["progress_pct"]
            if not isinstance(pct, int) or not (0 <= pct <= 100):
                raise TicketError("'progress_pct' phải là số nguyên từ 0 đến 100", 400, "INVALID_PROGRESS")
            updates["progress_pct"] = pct
        if "work_notes" in payload:
            updates["work_notes"] = str(payload["work_notes"]).strip()
        if "result_summary" in payload:
            updates["result_summary"] = str(payload["result_summary"]).strip()

        return self._record_mutation(
            ticket=ticket,
            actor=actor,
            extra_changes=updates,
            audit_event="ticket_status_changed",
            target_status="IN_PROGRESS",
        )

    def add_evidence(
        self,
        actor: Actor,
        ticket_id: str,
        payload: dict[str, Any],
        file_meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ticket = self.repo.get_ticket(ticket_id)
        if not ticket:
            raise TicketError("Không tìm thấy ticket", 404, "TICKET_NOT_FOUND")

        if actor.role == "TECHNICIAN":
            self._check_tech_write_scope(actor, ticket)
        elif actor.role not in {"ADMIN", "OPERATOR"}:
            raise TicketError("Không có quyền thêm bằng chứng", 403, "FORBIDDEN")

        raw_ver = payload.get("expected_version")
        expected_ver = int(raw_ver) if raw_ver is not None and str(raw_ver).strip() != "" else None
        self._check_version(ticket, expected_ver)

        if file_meta is not None:
            mime_type = (file_meta.get("mime_type") or "").lower()
            file_size = int(file_meta.get("file_size") or 0)
            file_name = (file_meta.get("file_name") or "").strip()
            if not file_name:
                raise TicketError("Thiếu tên tệp bằng chứng", 400, "MISSING_FILE_NAME")
            if mime_type not in ALLOWED_EVIDENCE_MIMES:
                raise TicketError(f"Loại tệp '{mime_type}' không được phép", 415, "UNSUPPORTED_MEDIA_TYPE")
            if file_size <= 0 or file_size > MAX_EVIDENCE_BYTES:
                raise TicketError("Kích thước tệp không hợp lệ hoặc vượt quá 10MB", 413, "FILE_TOO_LARGE")

        evidence = {
            "id": str(uuid4()),
            "ticket_id": ticket_id,
            "evidence_type": "FILE" if file_meta else (payload.get("evidence_type") or "NOTE"),
            "file_name": file_meta.get("file_name") if file_meta else None,
            "mime_type": file_meta.get("mime_type") if file_meta else None,
            "file_size": file_meta.get("file_size") if file_meta else None,
            "url": payload.get("url"),
            "note": (payload.get("note") or "").strip(),
            "uploaded_by": actor.user_id,
            "created_at": self._now(),
        }
        evidences = list(ticket.get("evidences", []))
        evidences.append(evidence)

        self._record_mutation(
            ticket=ticket,
            actor=actor,
            extra_changes={"evidences": evidences},
            audit_event="ticket_evidence_added",
            target_status=ticket["status"],
        )
        return evidence

    def submit_for_review(self, actor: Actor, ticket_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        ticket = self.repo.get_ticket(ticket_id)
        if not ticket:
            raise TicketError("Không tìm thấy ticket", 404, "TICKET_NOT_FOUND")
        self._check_tech_write_scope(actor, ticket)
        self._check_version(ticket, payload.get("expected_version"))

        return self._record_mutation(
            ticket=ticket,
            actor=actor,
            extra_changes={"progress_pct": 100},
            audit_event="ticket_status_changed",
            target_status="PENDING_REVIEW",
        )

    def review_ticket(self, actor: Actor, ticket_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Operator duyệt đóng (CLOSED) hoặc trả lại xử lý (IN_PROGRESS) kèm lý do."""
        self._check_operator_or_admin(actor, "duyệt hoặc trả lại ticket")
        ticket = self.repo.get_ticket(ticket_id)
        if not ticket:
            raise TicketError("Không tìm thấy ticket", 404, "TICKET_NOT_FOUND")
        self._check_version(ticket, payload.get("expected_version"))

        if ticket["status"] != "PENDING_REVIEW":
            raise TicketError(
                f"Chỉ có thể duyệt hoặc trả lại ticket ở trạng thái PENDING_REVIEW (hiện tại: {ticket['status']})",
                422,
                "NOT_PENDING_REVIEW",
            )

        decision = (payload.get("decision") or "").lower().strip()
        if decision == "approve":
            result_summary = (payload.get("result_summary") or ticket.get("result_summary") or "").strip()
            has_evidence = len(ticket.get("evidences", [])) > 0 or bool((ticket.get("work_notes") or "").strip())
            if not result_summary:
                raise TicketError("Thiếu 'result_summary' bắt buộc trước khi đóng ticket", 422, "MISSING_RESULT")
            if not has_evidence:
                raise TicketError("Thiếu bằng chứng hoặc ghi chú kết quả công việc trước khi đóng ticket", 422, "MISSING_EVIDENCE")

            # Lưu ý: KHÔNG chạm vào alert.status để giữ vòng đời ticket độc lập với cảnh báo.
            return self._record_mutation(
                ticket=ticket,
                actor=actor,
                extra_changes={"result_summary": result_summary, "return_reason": None},
                audit_event="ticket_closed",
                target_status="CLOSED",
            )

        if decision == "reject":
            reason = (payload.get("reason") or payload.get("return_reason") or "").strip()
            if not reason:
                raise TicketError("Bắt buộc nhập lý do trả lại xử lý ('reason')", 422, "MISSING_RETURN_REASON")
            return self._record_mutation(
                ticket=ticket,
                actor=actor,
                extra_changes={"return_reason": reason},
                audit_event="ticket_returned",
                target_status="IN_PROGRESS",
            )

        raise TicketError("'decision' phải là 'approve' hoặc 'reject'", 400, "INVALID_DECISION")