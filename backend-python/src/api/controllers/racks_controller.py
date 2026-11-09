from flask import Blueprint, jsonify, request

from src.api.middleware import require_auth
from src.domain.constants import Role
from src.domain.models.asset import Rack
from src.services.racks_service import RacksService
from src.services.session_service import SessionService


def rack_response(rack: Rack) -> dict:
    room = rack.room

    return {
        "id": rack.id,
        "roomId": rack.room_id,
        "code": rack.code,
        "name": rack.name,
        "capacityU": rack.capacity_u,
        "room": (
            {
                "id": room.id,
                "siteId": room.site_id,
                "code": room.code,
                "name": room.name,
            }
            if room is not None
            else None
        ),
    }


def create_racks_blueprint(
    racks_service: RacksService,
    session_service: SessionService,
) -> Blueprint:
    blueprint = Blueprint("racks", __name__, url_prefix="/racks")

    @blueprint.get("")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def list_racks():
        racks = racks_service.list_racks()

        return jsonify([
            rack_response(rack)
            for rack in racks
        ]), 200

    @blueprint.get("/<rack_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def get_rack(rack_id):
        rack, nodes = racks_service.get_details(rack_id)
        result = rack_response(rack)

        result["nodes"] = [
            {
                "id": node.id,
                "rackId": node.rack_id,
                "code": node.code,
                "name": node.name,
                "serialNumber": node.serial_number,
            }
            for node in nodes
        ]

        return jsonify(result), 200

    @blueprint.post("")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR, Role.OPERATOR),
    )
    def create_rack():
        rack = racks_service.create(
            request.get_json(silent=True)
        )

        return jsonify(rack_response(rack)), 201

    @blueprint.patch("/<rack_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR, Role.OPERATOR),
    )
    def update_rack(rack_id):
        rack = racks_service.update(
            rack_id,
            request.get_json(silent=True),
        )

        return jsonify(rack_response(rack)), 200

    @blueprint.delete("/<rack_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def delete_rack(rack_id):
        racks_service.delete(rack_id)

        return jsonify({
            "message": "Xóa Rack thành công",
        }), 200

    return blueprint