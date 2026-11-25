import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from src.api.controllers.audit_controller import create_audit_blueprint

from src.api.controllers.assets_controller import create_assets_blueprint
from src.api.controllers.auth_controller import create_auth_blueprint
from src.api.controllers.health_controller import health_bp
from src.api.controllers.markers_controller import create_markers_blueprint
from src.api.controllers.racks_controller import create_racks_blueprint
from src.api.controllers.rooms_controller import create_rooms_blueprint
from src.api.controllers.servers_controller import create_servers_blueprint
from src.api.controllers.sites_controller import create_sites_blueprint
from src.api.controllers.telemetry_controller import create_telemetry_blueprint
from src.api.controllers.telemetry_queries_controller import (
    create_telemetry_queries_blueprint,
)
from src.api.controllers.users_controller import create_users_blueprint
from src.api.docs import register_api_docs
from src.api.error_handlers import register_error_handlers
from src.dependency_container import build_container
from src.infrastructure.databases.database import Database
from src.api.controllers.alerts_controller import create_alerts_blueprint
from src.api.controllers.tickets_controller import create_tickets_blueprint


def create_app() -> Flask:
    backend_directory = Path(__file__).resolve().parent.parent
    load_dotenv(backend_directory / ".env")

    app = Flask(__name__)
    register_error_handlers(app)

    database_url = os.getenv("DATABASE_URL", "").strip()

    if not database_url:
        raise RuntimeError("Chưa cấu hình DATABASE_URL trong .env.")

    jwt_secret = os.getenv("JWT_SECRET", "")

    try:
        jwt_expires_in_seconds = int(
            os.getenv("JWT_EXPIRES_IN_SECONDS", "86400")
        )
    except ValueError as error:
        raise RuntimeError(
            "JWT_EXPIRES_IN_SECONDS phải là số nguyên."
        ) from error

    database = Database(database_url)

    container = build_container(
        database=database,
        jwt_secret=jwt_secret,
        jwt_expires_in_seconds=jwt_expires_in_seconds,
        stale_after_seconds=int(
            os.getenv("TELEMETRY_STALE_AFTER_SECONDS", "30")
        ),
        offline_after_seconds=int(
            os.getenv("TELEMETRY_OFFLINE_AFTER_SECONDS", "90")
        ),
        poll_interval_seconds=int(
            os.getenv("TELEMETRY_POLL_INTERVAL_SECONDS", "5")
        ),
    )
    app.register_blueprint(
    create_audit_blueprint(
        session_service=container.session_service,
        session_factory=database.create_session,
    )
)

    app.extensions["database"] = database
    app.extensions["container"] = container

    cors_origins = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3001",
        ).split(",")
        if origin.strip()
    ]

    CORS(
        app,
        resources={r"/*": {"origins": cors_origins}},
        allow_headers=["Content-Type", "Authorization"],
    )

    app.register_blueprint(health_bp)
    app.register_blueprint(
        create_alerts_blueprint(
            alert_service=container.alert_service,
            session_service=container.session_service,
        )
    )
    app.register_blueprint(
        create_auth_blueprint(
            login_service=container.login_service,
            session_service=container.session_service,
        )
    )

    app.register_blueprint(
        create_users_blueprint(
            users_service=container.users_service,
            session_service=container.session_service,
        )
    )

    app.register_blueprint(
        create_markers_blueprint(
            marker_service=container.marker_service,
            session_service=container.session_service,
        )
    )

    app.register_blueprint(
        create_assets_blueprint(
            assets_service=container.assets_service,
            session_service=container.session_service,
        )
    )

    app.register_blueprint(
        create_sites_blueprint(
            sites_service=container.sites_service,
            session_service=container.session_service,
        )
    )

    app.register_blueprint(
        create_rooms_blueprint(
            rooms_service=container.rooms_service,
            session_service=container.session_service,
        )
    )

    app.register_blueprint(
        create_racks_blueprint(
            racks_service=container.racks_service,
            session_service=container.session_service,
        )
    )

    app.register_blueprint(
        create_servers_blueprint(
            servers_service=container.servers_service,
            session_service=container.session_service,
        )
    )

    app.register_blueprint(
        create_telemetry_blueprint(
            telemetry_service=container.telemetry_service,
            session_service=container.session_service,
        )
    )

    app.register_blueprint(
        create_telemetry_queries_blueprint(
            query_service=container.telemetry_query_service,
            session_service=container.session_service,
        )
    )
    app.register_blueprint(
        create_tickets_blueprint(
            ticket_service=container.ticket_service,
            session_service=container.session_service,
        )
    )

    register_api_docs(app)

    return app