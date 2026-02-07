"""
JWT Authentication Middleware
Phase II - Todo Full-Stack Web Application

Validates JWT tokens issued by Better Auth and extracts user_id for request processing.
"""

from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get JWT secret from environment
# CRITICAL: This must match the NEXT_PUBLIC_BETTER_AUTH_SECRET in the frontend
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

if not BETTER_AUTH_SECRET:
    raise ValueError(
        "BETTER_AUTH_SECRET environment variable is not set. "
        "This must match the frontend secret for JWT validation."
    )


def get_current_user_id(request: Request) -> str:
    """
    Extract and validate JWT token from Authorization header.

    This dependency function is used in route handlers to authenticate requests.
    It extracts the JWT token, verifies its signature, and returns the user_id.

    Args:
        request: FastAPI request object containing headers

    Returns:
        str: Authenticated user's ID extracted from JWT token

    Raises:
        HTTPException(401): If token is missing, invalid, expired, or malformed

    Usage:
        @router.get("/api/tasks")
        async def get_tasks(user_id: str = Depends(get_current_user_id)):
            # user_id is guaranteed to be valid here
            pass

    Token Format:
        Authorization: Bearer <JWT_TOKEN>

    JWT Payload:
        {
            "sub": "user_id",
            "email": "user@example.com",
            "iat": 1234567890,
            "exp": 1234567890
        }
    """
    # Extract Authorization header
    auth_header: Optional[str] = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    # Check Bearer scheme
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'"
        )

    # Extract token
    token = auth_header.replace("Bearer ", "").strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing JWT token"
        )

    try:
        # Decode and verify JWT token
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        # Extract user ID from 'sub' claim
        # Better Auth typically stores user ID in the 'sub' (subject) claim
        user_id: Optional[str] = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing user ID"
            )

        return user_id

    except JWTError as e:
        # Token is expired, invalid signature, or malformed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}"
        )
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )


def get_optional_user_id(request: Request) -> Optional[str]:
    """
    Extract user_id from JWT token if present (optional authentication).

    Similar to get_current_user_id, but returns None instead of raising an exception
    if the token is missing or invalid. Useful for endpoints that work with or without
    authentication.

    Args:
        request: FastAPI request object containing headers

    Returns:
        Optional[str]: User ID if token is valid, None otherwise

    Usage:
        @router.get("/api/public-tasks")
        async def get_public_tasks(user_id: Optional[str] = Depends(get_optional_user_id)):
            if user_id:
                # User is authenticated
                pass
            else:
                # Anonymous user
                pass
    """
    try:
        return get_current_user_id(request)
    except HTTPException:
        return None


def verify_token(token: str) -> dict:
    """
    Verify JWT token and return its payload.

    This is a utility function for manual token verification outside of request context.

    Args:
        token: JWT token string (without 'Bearer ' prefix)

    Returns:
        dict: Decoded JWT payload

    Raises:
        JWTError: If token is invalid, expired, or malformed

    Usage:
        try:
            payload = verify_token(token)
            user_id = payload.get("sub")
        except JWTError:
            # Handle invalid token
            pass
    """
    return jwt.decode(
        token,
        BETTER_AUTH_SECRET,
        algorithms=[JWT_ALGORITHM]
    )


def create_test_token(user_id: str, expiration_days: int = 7) -> str:
    """
    Create a test JWT token for development and testing.

    WARNING: This should only be used for testing. In production, tokens are issued
    by Better Auth on the frontend.

    Args:
        user_id: User ID to encode in the token
        expiration_days: Token validity period in days

    Returns:
        str: JWT token string

    Usage:
        token = create_test_token("user123")
        headers = {"Authorization": f"Bearer {token}"}
    """
    from datetime import datetime, timedelta

    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=expiration_days)
    }

    return jwt.encode(payload, BETTER_AUTH_SECRET, algorithm=JWT_ALGORITHM)


# Alias for compatibility with chat routes
get_current_user = get_current_user_id
