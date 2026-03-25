"""
Python DevOps Reference Application.

A showcase Flask application demonstrating DevOps best practices
with structured logging, authentication, monitoring, and IaC.
"""
import os
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import get_config
from utils import setup_logging
from routes.health import health
from routes.api import api


def create_app(config=None, config_object=None):
    """
    Application factory function.

    Args:
        config: Backward-compatible config object argument.
        config_object: Preferred config object argument.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    # Load configuration
    if config_object is None:
        config_object = config
    if config_object is None:
        config_object = get_config()
    app.config.from_object(config_object)

    # Setup logging
    setup_logging(
        app,
        log_level=app.config.get('LOG_LEVEL', 'INFO'),
        log_format=app.config.get('LOG_FORMAT', 'json')
    )

    # Initialize rate limiter
    if app.config.get('RATELIMIT_ENABLED', True):
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[app.config.get('RATELIMIT_DEFAULT', '100/hour')],
            storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
        )
        app.extensions['limiter'] = limiter

    # Register blueprints
    app.register_blueprint(health)
    app.register_blueprint(api)

    # Error handlers
    @app.errorhandler(404)  # type: ignore[misc]
    def not_found(_error):
        """Handle 404 errors."""
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)  # type: ignore[misc]
    def internal_error(error):
        """Handle 500 errors."""
        app.logger.error(f"Internal server error: {str(error)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

    @app.before_request
    def before_request():
        """Log incoming requests."""
        app.logger.debug(f"{request.method} {request.path}")

    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    # For local dev only; in Docker we'll use gunicorn
    app.run(
        host="0.0.0.0",
        port=int(os.getenv('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
