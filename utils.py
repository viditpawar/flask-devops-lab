"""
Utility modules for authentication, logging, and monitoring.
"""
import json
import logging
from datetime import datetime, timezone
from functools import wraps
from typing import Callable

from flask import current_app, g, jsonify, request
from werkzeug.exceptions import BadRequest


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


def setup_logging(app, log_level: str = "INFO", log_format: str = "json"):
    """
    Configure application logging.

    Args:
        app: Flask application instance.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Log format ('json' or 'text').
    """
    app.logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setLevel(log_level)

    if log_format == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)


def require_api_key(func: Callable) -> Callable:
    """
    Decorator to require API key for protected endpoints.

    API key should be provided in the X-API-Key header.
    """

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_app.config.get("ENABLE_AUTH", False):
            return func(*args, **kwargs)

        api_key = request.headers.get(current_app.config.get("API_KEY_HEADER", "X-API-Key"))
        if not api_key:
            current_app.logger.warning(
                f"Unauthorized access attempt to {request.path}",
                extra={"ip": request.remote_addr},
            )
            return jsonify({"error": "API key required"}), 401

        valid_key = current_app.config.get("VALID_API_KEY", "default-key")
        if api_key != valid_key:
            current_app.logger.warning(
                f"Invalid API key used for {request.path}",
                extra={"ip": request.remote_addr},
            )
            return jsonify({"error": "Invalid API key"}), 403

        g.api_key = api_key
        return func(*args, **kwargs)

    return decorated_function


def log_request(func: Callable) -> Callable:
    """Decorator to log incoming requests."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        current_app.logger.info(
            f"{request.method} {request.path}",
            extra={
                "method": request.method,
                "path": request.path,
                "ip": request.remote_addr,
                "user_agent": request.user_agent.string,
            },
        )
        return func(*args, **kwargs)

    return decorated_function


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle common errors and return proper responses."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BadRequest:
            current_app.logger.warning("Invalid JSON body")
            return jsonify({"error": "Invalid JSON body"}), 400
        except ValueError as error:
            current_app.logger.warning(f"Validation error: {str(error)}")
            return jsonify({"error": str(error)}), 400
        except Exception as error:  # pylint: disable=broad-except
            current_app.logger.error(f"Unexpected error: {str(error)}", exc_info=True)
            return jsonify({"error": "Internal server error"}), 500

    return decorated_function
