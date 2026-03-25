"""
Main API endpoints.
"""
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from pydantic import BaseModel, ValidationError, field_validator
from werkzeug.exceptions import BadRequest

from utils import handle_errors, log_request, require_api_key

api = Blueprint("api", __name__, url_prefix="/api/v1")


class GreetingRequest(BaseModel):
    """Request model for greeting endpoint."""

    name: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value: str) -> str:
        """Validate that name is not empty."""
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 100:
            raise ValueError("Name must be 100 characters or less")
        return value.strip()


@api.route("/hello/<name>", methods=["GET"])
@log_request
@handle_errors
def hello(name: str):
    """
    Greet a user by name.

    Args:
        name: The name to greet.

    Returns:
        JSON response with greeting message.
    """
    if not name or not name.strip():
        return jsonify({"error": "Name cannot be empty"}), 400
    if len(name) > 100:
        return jsonify({"error": "Name must be 100 characters or less"}), 400

    clean_name = name.strip()
    current_app.logger.info(f"Greeting request for: {clean_name}")
    return jsonify(
        {
            "message": f"Hello, {clean_name}!",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    ), 200


@api.route("/hello", methods=["POST"])
@require_api_key
@log_request
@handle_errors
def hello_post():
    """
    Greet a user via POST request with JSON body.

    Requirements:
        If ENABLE_AUTH is True, requires X-API-Key header.

    Request body:
        {
            "name": "string"
        }

    Returns:
        JSON response with greeting message.
    """
    try:
        data = request.get_json() or {}
        request_data = GreetingRequest(**data)
        current_app.logger.info(f"Greeting POST request for: {request_data.name}")
        return jsonify(
            {
                "message": f"Hello, {request_data.name}!",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ), 200
    except BadRequest:
        current_app.logger.warning("Invalid JSON payload for /api/v1/hello")
        return jsonify({"error": "Invalid JSON body"}), 400
    except ValidationError as error:
        current_app.logger.warning(f"Validation error: {error.json()}")
        details = error.errors(include_context=False)
        return jsonify({"error": "Invalid request", "details": details}), 400


@api.route("/info", methods=["GET"])
@handle_errors
def info():
    """
    Get application information.

    Returns:
        JSON with application metadata and configuration info.
    """
    return jsonify(
        {
            "app": "python-devops-reference-app",
            "version": "1.0.0",
            "environment": current_app.config.get("FLASK_ENV", "unknown"),
            "debug": current_app.debug,
            "auth_enabled": current_app.config.get("ENABLE_AUTH", False),
        }
    ), 200
