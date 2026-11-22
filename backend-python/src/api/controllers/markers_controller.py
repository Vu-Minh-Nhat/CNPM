from flask import Blueprint, jsonify, request

from src.api.middleware import require_auth
from src.domain.constants import Role
from src.services.marker_service import MarkerService
from src.services.session_service import SessionService


def create_markers_blueprint(
    marker_service: MarkerService,
    session_service: SessionService,
) -> Blueprint:
    blueprint = Blueprint("markers", __name__, url_prefix="/markers")

    @blueprint.post("")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def register_marker():
        payload = request.get_json(silent=True) or {}

        try:
            marker = marker_service.register_marker(
                marker_type=payload.get("marker_type", ""),
                identifier=payload.get("identifier", ""),
                node_id=payload.get("node_id", ""),
            )
        except ValueError as exc:
            message = str(exc)

            if message == "Active marker identifier already exists":
                return jsonify({
                    "error": "Conflict",
                    "message": message,
                    "statusCode": 409,
                }), 409

            return jsonify({
                "error": "Bad Request",
                "message": message,
                "statusCode": 400,
            }), 400

        return jsonify(marker), 201

    @blueprint.get("/lookup")
    @require_auth(
        session_service=session_service,
        allowed_roles=(
            Role.ADMINISTRATOR,
            Role.OPERATOR,
            Role.TECHNICIAN,
        ),
    )
    def lookup_marker():
        result = marker_service.lookup_marker(
            marker_type=request.args.get("marker_type", ""),
            identifier=request.args.get("identifier", ""),
        )

        if result is None:
            return jsonify(
                {"message": "Marker not found or inactive"}
            ), 404

        marker, node = result

        return jsonify(
            {
                "marker": marker,
                "node": node,
            }
        ), 200

    @blueprint.patch("/<marker_id>/deactivate")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def deactivate_marker(marker_id):
        marker = marker_service.deactivate_marker(marker_id)

        return jsonify(marker), 200

    @blueprint.get("")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def list_markers():
        return jsonify(marker_service.list_markers()), 200

    return blueprint