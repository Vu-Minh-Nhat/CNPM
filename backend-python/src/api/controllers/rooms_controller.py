from flask import Blueprint, jsonify, request

from src.api.middleware import require_auth
from src.domain.constants import Role
from src.domain.models.asset import Room
from src.services.rooms_service import RoomsService
from src.services.session_service import SessionService


def room_response(room: Room) -> dict:
    site = room.site

    return {
        "id": room.id,
        "siteId": room.site_id,
        "code": room.code,
        "name": room.name,
        "site": (
            {
                "id": site.id,
                "code": site.code,
                "name": site.name,
            }
            if site is not None
            else None
        ),
    }


def create_rooms_blueprint(
    rooms_service: RoomsService,
    session_service: SessionService,
) -> Blueprint:
    blueprint = Blueprint("rooms", __name__, url_prefix="/rooms")

    @blueprint.get("")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def list_rooms():
        rooms = rooms_service.list_rooms()

        return jsonify([
            room_response(room)
            for room in rooms
        ]), 200

    @blueprint.get("/<room_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def get_room(room_id):
        room, racks = rooms_service.get_details(room_id)
        result = room_response(room)

        result["racks"] = [
            {
                "id": rack.id,
                "roomId": rack.room_id,
                "code": rack.code,
                "name": rack.name,
                "capacityU": rack.capacity_u,
            }
            for rack in racks
        ]

        return jsonify(result), 200

    @blueprint.post("")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR, Role.OPERATOR),
    )
    def create_room():
        room = rooms_service.create(
            request.get_json(silent=True)
        )

        return jsonify(room_response(room)), 201

    @blueprint.patch("/<room_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR, Role.OPERATOR),
    )
    def update_room(room_id):
        room = rooms_service.update(
            room_id,
            request.get_json(silent=True),
        )

        return jsonify(room_response(room)), 200

    @blueprint.delete("/<room_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def delete_room(room_id):
        rooms_service.delete(room_id)

        return jsonify({
            "message": "Xóa Room thành công",
        }), 200

    return blueprint