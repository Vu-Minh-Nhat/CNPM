from flask import jsonify
from flask_swagger_ui import get_swaggerui_blueprint

from src.api.openapi import build_openapi


def register_api_docs(app):
    @app.get("/openapi.json")
    def openapi_document():
        return jsonify(build_openapi())

    swagger_blueprint = get_swaggerui_blueprint(
        "/docs",
        "/openapi.json",
        config={
            "app_name": "AR-IMMS Backend Python",
            "validatorUrl": None,
            "persistAuthorization": False,
        },
    )

    app.register_blueprint(swagger_blueprint)