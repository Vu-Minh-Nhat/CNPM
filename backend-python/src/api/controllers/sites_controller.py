from flask import Blueprint, jsonify, request

from src.api.middleware import require_auth
from src.domain.constants import Role
from src.domain.models.asset import Site
from src.services.session_service import SessionService
from src.services.sites_service import SitesService


def site_response(site: Site) -> dict:
    return {
        "id": site.id,
        "code": site.code,
        "name": site.name,
    }


def create_sites_blueprint(
    sites_service: SitesService,
    session_service: SessionService,
) -> Blueprint:
    blueprint = Blueprint("sites", __name__, url_prefix="/sites")

    @blueprint.get("")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def list_sites():
        sites = sites_service.list_sites()

        return jsonify([
            site_response(site)
            for site in sites
        ]), 200

    @blueprint.get("/<site_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=tuple(Role),
    )
    def get_site(site_id):
        site = sites_service.get_site(site_id)
        return jsonify(site_response(site)), 200

    @blueprint.post("")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR, Role.OPERATOR),
    )
    def create_site():
        site = sites_service.create(
            request.get_json(silent=True)
        )

        return jsonify(site_response(site)), 201

    @blueprint.patch("/<site_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR, Role.OPERATOR),
    )
    def update_site(site_id):
        site = sites_service.update(
            site_id,
            request.get_json(silent=True),
        )

        return jsonify(site_response(site)), 200

    @blueprint.delete("/<site_id>")
    @require_auth(
        session_service=session_service,
        allowed_roles=(Role.ADMINISTRATOR,),
    )
    def delete_site(site_id):
        sites_service.delete(site_id)

        return jsonify({
            "message": "Xóa Site thành công",
        }), 200

    return blueprint