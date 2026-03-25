"""
Comprehensive test suite for the Flask application.
"""
import json

import pytest

from app import create_app
from config import DevelopmentConfig


@pytest.fixture
def app():
    """Create application for testing."""
    flask_app = create_app(config=DevelopmentConfig())
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data

    def test_health_check_with_slash(self, client):
        response = client.get("/health/")
        assert response.status_code == 200
        assert response.get_json()["status"] == "healthy"

    def test_readiness_check(self, client):
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.get_json()["ready"] is True

    def test_liveness_check(self, client):
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.get_json()["alive"] is True


class TestAPIEndpoints:
    """Test API endpoints."""

    def test_hello_get_valid_name(self, client):
        response = client.get("/api/v1/hello/John")
        assert response.status_code == 200
        data = response.get_json()
        assert "Hello, John" in data["message"]
        assert "timestamp" in data

    def test_hello_get_empty_name(self, client):
        response = client.get("/api/v1/hello/")
        assert response.status_code == 404  # Route not matched

    def test_hello_post_valid_request(self, client):
        response = client.post(
            "/api/v1/hello",
            data=json.dumps({"name": "Alice"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "Hello, Alice" in data["message"]
        assert "timestamp" in data

    def test_hello_post_missing_name(self, client):
        response = client.post(
            "/api/v1/hello",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_hello_post_empty_name(self, client):
        response = client.post(
            "/api/v1/hello",
            data=json.dumps({"name": ""}),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_hello_post_name_too_long(self, client):
        long_name = "a" * 101
        response = client.post(
            "/api/v1/hello",
            data=json.dumps({"name": long_name}),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_hello_post_whitespace_name(self, client):
        response = client.post(
            "/api/v1/hello",
            data=json.dumps({"name": "   "}),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_info_endpoint(self, client):
        response = client.get("/api/v1/info")
        assert response.status_code == 200
        data = response.get_json()
        assert data["app"] == "python-devops-reference-app"
        assert "version" in data
        assert "environment" in data
        assert "debug" in data
        assert "auth_enabled" in data


class TestAuthenticationDevEnvironment:
    """Test authentication in development environment (auth disabled)."""

    def test_post_without_api_key_auth_disabled(self, client):
        response = client.post(
            "/api/v1/hello",
            data=json.dumps({"name": "Bob"}),
            content_type="application/json",
        )
        assert response.status_code == 200  # Allowed because auth disabled


class TestErrorHandling:
    """Test error handling."""

    def test_not_found_error(self, client):
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_invalid_json(self, client):
        response = client.post(
            "/api/v1/hello",
            data="invalid json",
            content_type="application/json",
        )
        assert response.status_code == 400


class TestRequestResponse:
    """Test request and response handling."""

    def test_response_content_type(self, client):
        response = client.get("/health")
        assert response.content_type == "application/json"

    def test_request_logging(self, client):
        response = client.get("/api/v1/hello/TestUser")
        assert response.status_code == 200

    def test_special_characters_in_name(self, client):
        response = client.get("/api/v1/hello/John%20Doe")
        assert response.status_code == 200
        data = response.get_json()
        assert "John Doe" in data["message"] or "John%20Doe" in data["message"]
