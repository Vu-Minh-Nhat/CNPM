import os
from src.api.controllers.users_controller import create_users_blueprint
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from src.api.controllers.auth_controller import create_auth_blueprint
from src.api.controllers.health_controller import health_bp
from src.dependency_container import build_container
from src.infrastructure.databases.database import Database


def create_app() -> Flask:
    backend_directory = Path(__file__).resolve().parent.parent
    load_dotenv(backend_directory / ".env")

    app = Flask(__name__)

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
    return app