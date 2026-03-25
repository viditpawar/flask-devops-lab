"""
Health check endpoints for monitoring application status.
"""
import os

from flask import Blueprint, current_app, jsonify

try:
    import psutil
except ImportError:  # pragma: no cover - handled at runtime
    psutil = None

health = Blueprint("health", __name__, url_prefix="/health")


@health.route("", methods=["GET"])
@health.route("/", methods=["GET"])
def health_check():
    """
    Application health check endpoint.

    Returns:
        JSON with health status and optional system metrics.
    """
    response = {
        "status": "healthy",
        "service": "python-devops-reference-app",
        "version": "1.0.0",
    }

    try:
        if current_app.config.get("ENABLE_MONITORING", True) and psutil is not None:
            disk_root = os.path.abspath(os.sep)
            response["metrics"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage(disk_root).percent,
            }
    except Exception as error:
        current_app.logger.warning(f"Could not gather system metrics: {str(error)}")

    return jsonify(response), 200


@health.route("/ready", methods=["GET"])
def readiness_check():
    """
    Readiness probe for Kubernetes/container orchestration.

    Indicates if the application is ready to accept traffic.
    """
    return jsonify({"ready": True}), 200


@health.route("/live", methods=["GET"])
def liveness_check():
    """
    Liveness probe for Kubernetes/container orchestration.

    Indicates if the application is alive and responsive.
    """
    return jsonify({"alive": True}), 200
