from __future__ import annotations

from flask import Blueprint, jsonify, request
from src.services.ticket_service import Actor, TicketError, TicketService


OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {"title": "AR-IMMS Maintenance Ticket API", "version": "1.0.0"},
    "paths": {
        "/tickets": {
            "get": {"summary": "Danh sách ticket theo phạm vi quyền"},
            "post": {"summary": "Tạo ticket thủ công hoặc từ cảnh báo (kiểm tra khớp Node)"},
        },
        "/tickets/{ticket_id}": {"get": {"summary": "Chi tiết ticket kèm lịch sử thao tác"}},
        "/tickets/{ticket_id}/assign": {"post": {"summary": "Phân công Technician đang hoạt động"}},
        "/tickets/{ticket_id}/start": {"post": {"summary": "Technician bắt đầu xử lý"}},
        "/tickets/{ticket_id}/work": {"patch": {"summary": "Cập nhật tiến độ và nội dung xử lý"}},
        "/tickets/{ticket_id}/evidences": {"post": {"summary": "Thêm bằng chứng (kiểm tra loại/kích thước tệp & quyền)"}},
        "/tickets/{ticket_id}/submit-review": {"post": {"summary": "Gửi ticket sang chờ duyệt (PENDING_REVIEW)"}},
        "/tickets/{ticket_id}/review": {"post": {"summary": "Operator duyệt đóng (CLOSED) hoặc trả lại (IN_PROGRESS) kèm lý do"}},
    },
}


def _actor_from_request() -> Actor:
    user_id = (request.headers.get("X-User-Id") or "").strip()
    role = (request.headers.get("X-User-Role") or "").strip().upper()
    if not user_id or not role:
        raise TicketError("Thiếu thông tin xác thực (X-User-Id, X-User-Role)", 401, "UNAUTHORIZED")
    raw_nodes = request.headers.get("X-Allowed-Nodes") or ""
    allowed_nodes = {n.strip() for n in raw_nodes.split(",") if n.strip()}
    return Actor(user_id=user_id, role=role, allowed_node_ids=allowed_nodes)


def create_tickets_blueprint(service: TicketService) -> Blueprint:
    bp = Blueprint("tickets", __name__)

    @bp.errorhandler(TicketError)
    def _handle_ticket_error(err: TicketError):
        return jsonify({"error": err.code, "message": err.message}), err.status_code

    @bp.get("/tickets/openapi.json")
    def openapi_doc():
        return jsonify(OPENAPI_SPEC), 200

    @bp.get("/tickets")
    def list_tickets():
        actor = _actor_from_request()
        filters = {
            "status": request.args.get("status"),
            "node_id": request.args.get("node_id"),
            "assignee_id": request.args.get("assignee_id"),
        }
        return jsonify({"items": service.list_tickets(actor, filters)}), 200

    @bp.post("/tickets")
    def create_ticket():
        actor = _actor_from_request()
        data = request.get_json(silent=True) or {}
        ticket = service.create_ticket(actor, data)
        return jsonify(ticket), 201

    @bp.get("/tickets/<ticket_id>")
    def get_ticket(ticket_id: str):
        actor = _actor_from_request()
        return jsonify(service.get_ticket(actor, ticket_id)), 200

    @bp.post("/tickets/<ticket_id>/assign")
    def assign_ticket(ticket_id: str):
        actor = _actor_from_request()
        data = request.get_json(silent=True) or {}
        return jsonify(service.assign_ticket(actor, ticket_id, data)), 200

    @bp.post("/tickets/<ticket_id>/start")
    def start_ticket(ticket_id: str):
        actor = _actor_from_request()
        data = request.get_json(silent=True) or {}
        return jsonify(service.start_work(actor, ticket_id, data)), 200

    @bp.patch("/tickets/<ticket_id>/work")
    def update_ticket_work(ticket_id: str):
        actor = _actor_from_request()
        data = request.get_json(silent=True) or {}
        return jsonify(service.update_work(actor, ticket_id, data)), 200

    @bp.post("/tickets/<ticket_id>/evidences")
    def add_ticket_evidence(ticket_id: str):
        actor = _actor_from_request()
        file_meta = None
        if "file" in request.files:
            f = request.files["file"]
            raw = f.read()
            file_meta = {
                "file_name": f.filename,
                "mime_type": f.mimetype,
                "file_size": len(raw),
            }
            payload = dict(request.form)
        else:
            payload = request.get_json(silent=True) or {}
        evidence = service.add_evidence(actor, ticket_id, payload, file_meta=file_meta)
        return jsonify(evidence), 201

    @bp.post("/tickets/<ticket_id>/submit-review")
    def submit_ticket_review(ticket_id: str):
        actor = _actor_from_request()
        data = request.get_json(silent=True) or {}
        return jsonify(service.submit_for_review(actor, ticket_id, data)), 200

    @bp.post("/tickets/<ticket_id>/review")
    def review_ticket(ticket_id: str):
        actor = _actor_from_request()
        data = request.get_json(silent=True) or {}
        return jsonify(service.review_ticket(actor, ticket_id, data)), 200

    return bp