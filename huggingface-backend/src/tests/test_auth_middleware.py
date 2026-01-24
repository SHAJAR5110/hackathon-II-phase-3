"""
Tests for authentication and authorization middleware
Verifies:
- Requests without auth header return 401
- Valid auth headers pass through
- User_id is attached to request state
- Structured error responses
"""

import pytest
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from ..middleware.auth import auth_middleware, get_current_user, validate_user_id
from ..middleware.errors import error_handling_middleware
from ..middleware.logging_middleware import logging_middleware


# Create a test app with middleware
def create_test_app():
    app = FastAPI()

    # Register middleware
    app.middleware("http")(error_handling_middleware)
    app.middleware("http")(auth_middleware)
    app.middleware("http")(logging_middleware)

    # Protected endpoint that requires user_id
    @app.get("/protected")
    async def protected_endpoint(user_id: str = Depends(get_current_user)):
        return {"user_id": user_id}

    # Public endpoint (no auth required)
    @app.get("/public")
    async def public_endpoint():
        return {"message": "public"}

    return app


@pytest.fixture
def client():
    """Create test client"""
    app = create_test_app()
    return TestClient(app)


class TestValidateUserId:
    """Test user_id validation"""

    def test_valid_user_id_simple(self):
        """Test simple alphanumeric user_id"""
        assert validate_user_id("user123") is True

    def test_valid_user_id_with_special_chars(self):
        """Test user_id with allowed special characters"""
        assert validate_user_id("user_123.test-id") is True

    def test_invalid_empty_string(self):
        """Test that empty string is invalid"""
        assert validate_user_id("") is False

    def test_invalid_none(self):
        """Test that None is invalid"""
        assert validate_user_id(None) is False

    def test_invalid_too_long(self):
        """Test that exceeding max length is invalid"""
        assert validate_user_id("a" * 256) is False

    def test_invalid_special_chars(self):
        """Test that invalid special characters are rejected"""
        assert validate_user_id("user@domain.com") is False
        assert validate_user_id("user#123") is False


class TestAuthMiddleware:
    """Test authentication middleware"""

    def test_public_endpoint_no_auth(self, client):
        """Public endpoints accessible without auth"""
        response = client.get("/public")
        assert response.status_code == 200
        assert response.json() == {"message": "public"}

    def test_protected_endpoint_no_auth(self, client):
        """Protected endpoints blocked without auth"""
        response = client.get("/protected")
        assert response.status_code == 401
        assert "Unauthorized" in response.json()["detail"]

    def test_protected_endpoint_with_valid_auth(self, client):
        """Protected endpoints accessible with valid auth"""
        headers = {"Authorization": "Bearer user123"}
        response = client.get("/protected", headers=headers)
        assert response.status_code == 200
        assert response.json() == {"user_id": "user123"}

    def test_invalid_auth_format_missing_bearer(self, client):
        """Invalid auth format rejected (missing Bearer)"""
        headers = {"Authorization": "user123"}
        response = client.get("/protected", headers=headers)
        assert response.status_code == 401

    def test_invalid_auth_format_extra_parts(self, client):
        """Invalid auth format rejected (too many parts)"""
        headers = {"Authorization": "Bearer user123 extra"}
        response = client.get("/protected", headers=headers)
        assert response.status_code == 401

    def test_invalid_user_id_format(self, client):
        """Invalid user_id format rejected"""
        headers = {"Authorization": "Bearer user@domain.com"}
        response = client.get("/protected", headers=headers)
        assert response.status_code == 401

    def test_empty_user_id(self, client):
        """Empty user_id rejected"""
        headers = {"Authorization": "Bearer "}
        response = client.get("/protected", headers=headers)
        assert response.status_code == 401

    def test_case_insensitive_bearer(self, client):
        """Bearer keyword is case insensitive"""
        headers = {"Authorization": "bearer user123"}
        response = client.get("/protected", headers=headers)
        assert response.status_code == 200

    def test_request_id_in_response_headers(self, client):
        """Response includes request_id header"""
        headers = {"Authorization": "Bearer user123"}
        response = client.get("/protected", headers=headers)
        assert "x-request-id" in response.headers
        assert response.headers["x-request-id"]  # Not empty


class TestErrorHandling:
    """Test error handling middleware"""

    def test_error_response_structure(self, client):
        """Error responses have required structure"""
        response = client.get("/protected")
        assert response.status_code == 401
        data = response.json()
        assert "error" in data or "detail" in data
        assert response.headers.get("x-request-id")  # request_id present


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
