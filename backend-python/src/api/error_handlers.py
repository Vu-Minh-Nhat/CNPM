from flask import Flask, jsonify

from src.domain.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ValidationError)
    def handle_validation(error):
        return jsonify({
            "message": str(error),
            "error": "Bad Request",
            "statusCode": 400,
        }), 400

    @app.errorhandler(ResourceNotFoundError)
    def handle_not_found(error):
        return jsonify({
            "message": str(error),
            "error": "Not Found",
            "statusCode": 404,
        }), 404

    @app.errorhandler(ResourceConflictError)
    def handle_conflict(error):
        return jsonify({
            "message": str(error),
            "error": "Conflict",
            "statusCode": 409,
        }), 409