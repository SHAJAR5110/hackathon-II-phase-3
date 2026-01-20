"""
Authentication Endpoint Tests
Phase II - Todo Full-Stack Web Application

Tests for POST /auth/signup, POST /auth/signin, and POST /auth/logout endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio

from main import app
from db import get_session
from models import User


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_session():
    """
    Create a test database session for each test.
    Uses in-memory SQLite database.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
def client(test_session):
    """
    Create a test client for API requests.
    """
    def override_get_session():
        return test_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ============================================================================
# Signup Tests (POST /auth/signup)
# ============================================================================

def test_signup_success(client):
    """
    Test successful user signup with valid data.
    Should return 201 with user data and JWT token.
    """
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "name": "Test User"
        }
    )

    assert response.status_code == 201
    data = response.json()

    # Verify response structure
    assert "user" in data
    assert "token" in data
    assert "expires_in" in data

    # Verify user data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["name"] == "Test User"
    assert "id" in data["user"]
    assert "created_at" in data["user"]

    # Verify token is a non-empty string
    assert isinstance(data["token"], str)
    assert len(data["token"]) > 0

    # Verify expires_in is 7 days (604800 seconds)
    assert data["expires_in"] == 604800


def test_signup_email_already_exists(client):
    """
    Test signup with an email that already exists.
    Should return 409 Conflict.
    """
    # Create first user
    client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "name": "Test User"
        }
    )

    # Attempt to create second user with same email
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "DifferentPass456",
            "name": "Another User"
        }
    )

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_signup_invalid_email_format(client):
    """
    Test signup with invalid email format.
    Should return 400 Bad Request.
    """
    response = client.post(
        "/auth/signup",
        json={
            "email": "invalid-email",
            "password": "SecurePass123",
            "name": "Test User"
        }
    )

    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


def test_signup_weak_password_too_short(client):
    """
    Test signup with password shorter than 8 characters.
    Should return 400 Bad Request.
    """
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "Short1",
            "name": "Test User"
        }
    )

    assert response.status_code == 400
    assert "password" in response.json()["detail"].lower()


def test_signup_weak_password_no_uppercase(client):
    """
    Test signup with password missing uppercase letter.
    Should return 400 Bad Request.
    """
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "lowercase123",
            "name": "Test User"
        }
    )

    assert response.status_code == 400
    assert "uppercase" in response.json()["detail"].lower()


def test_signup_weak_password_no_lowercase(client):
    """
    Test signup with password missing lowercase letter.
    Should return 400 Bad Request.
    """
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "UPPERCASE123",
            "name": "Test User"
        }
    )

    assert response.status_code == 400
    assert "lowercase" in response.json()["detail"].lower()


def test_signup_weak_password_no_number(client):
    """
    Test signup with password missing number.
    Should return 400 Bad Request.
    """
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "SecurePass",
            "name": "Test User"
        }
    )

    assert response.status_code == 400
    assert "number" in response.json()["detail"].lower()


def test_signup_empty_name(client):
    """
    Test signup with empty name.
    Should return 400 Bad Request.
    """
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "name": ""
        }
    )

    assert response.status_code == 400
    assert "name" in response.json()["detail"].lower()


def test_signup_missing_fields(client):
    """
    Test signup with missing required fields.
    Should return 400 Bad Request.
    """
    response = client.post(
        "/auth/signup",
        json={"email": "test@example.com"}
    )

    assert response.status_code == 400


# ============================================================================
# Signin Tests (POST /auth/signin)
# ============================================================================

def test_signin_success(client):
    """
    Test successful user signin with valid credentials.
    Should return 200 with user data and JWT token.
    """
    # Create user
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "name": "Test User"
        }
    )
    assert signup_response.status_code == 201

    # Sign in
    response = client.post(
        "/auth/signin",
        json={
            "email": "test@example.com",
            "password": "SecurePass123"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "user" in data
    assert "token" in data
    assert "expires_in" in data

    # Verify user data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["name"] == "Test User"

    # Verify token is a non-empty string
    assert isinstance(data["token"], str)
    assert len(data["token"]) > 0


def test_signin_invalid_email(client):
    """
    Test signin with email that doesn't exist.
    Should return 401 Unauthorized.
    """
    response = client.post(
        "/auth/signin",
        json={
            "email": "nonexistent@example.com",
            "password": "SecurePass123"
        }
    )

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_signin_invalid_password(client):
    """
    Test signin with incorrect password.
    Should return 401 Unauthorized.
    """
    # Create user
    client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "name": "Test User"
        }
    )

    # Attempt signin with wrong password
    response = client.post(
        "/auth/signin",
        json={
            "email": "test@example.com",
            "password": "WrongPassword456"
        }
    )

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_signin_invalid_email_format(client):
    """
    Test signin with invalid email format.
    Should return 400 Bad Request.
    """
    response = client.post(
        "/auth/signin",
        json={
            "email": "invalid-email",
            "password": "SecurePass123"
        }
    )

    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


def test_signin_missing_fields(client):
    """
    Test signin with missing required fields.
    Should return 400 Bad Request.
    """
    response = client.post(
        "/auth/signin",
        json={"email": "test@example.com"}
    )

    assert response.status_code == 400


# ============================================================================
# Logout Tests (POST /auth/logout)
# ============================================================================

def test_logout_success(client):
    """
    Test logout endpoint.
    Should return 200 with success message.
    """
    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert "message" in response.json()
    assert "logout successful" in response.json()["message"].lower()


# ============================================================================
# JWT Token Validation Tests
# ============================================================================

def test_jwt_token_contains_correct_claims(client):
    """
    Test that JWT token contains expected claims (sub, email, iat, exp).
    """
    from jose import jwt
    import os

    # Create user and get token
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "name": "Test User"
        }
    )

    token = response.json()["token"]

    # Decode token (without verification for testing)
    secret = os.getenv("BETTER_AUTH_SECRET", "test-secret")
    payload = jwt.decode(token, secret, algorithms=["HS256"])

    # Verify claims exist
    assert "sub" in payload  # User ID
    assert "email" in payload  # Email
    assert "iat" in payload  # Issued at
    assert "exp" in payload  # Expiration

    # Verify email matches
    assert payload["email"] == "test@example.com"
