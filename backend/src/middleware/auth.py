"""
Authentication middleware and authorization dependency for FastAPI
- Validates user_id from Authorization header (Better Auth session token)
- Extracts and validates user_id, attaches to request.state
- Provides get_current_user() dependency for protected endpoints
"""

import re

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthCredentials, HTTPBearer

from ..logging_config import get_logger

logger = get_logger(__name__)

# HTTP Bearer scheme for auth header
security = HTTPBearer(auto_error=False)


def validate_user_id(user_id: str) -> bool:
    """
    Validate user_id format
    - Non-empty string
    - Alphanumeric, hyphens, underscores, dots allowed
    - Max 255 characters
    """
    if not user_id or not isinstance(user_id, str):
        return False
    if len(user_id) > 255:
        return False
    # Allow alphanumeric, hyphens, underscores, dots
    pattern = r"^[a-zA-Z0-9._-]+$"
    return bool(re.match(pattern, user_id))


async def auth_middleware(request: Request, call_next):
    """
    Middleware to extract and validate user_id from Authorization header
    Attaches user_id to request.state for use in endpoints
    Returns 401 for missing/invalid auth

    Expected header format: Authorization: Bearer <user_id>
    Or simpler: Authorization: Bearer <session_token> (extract user_id from token)
    """
    request.state.user_id = None
    request.state.request_id = getattr(request.state, "request_id", "unknown")

    # Get Authorization header
    auth_header = request.headers.get("Authorization", "").strip()

    if not auth_header:
        logger.warning(
            "Missing authorization header",
            path=request.url.path,
            method=request.method,
            request_id=request.state.request_id,
        )
        raise create_unauthorized_response()

    # Parse Bearer token
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(
            "Invalid authorization header format",
            path=request.url.path,
            method=request.method,
            auth_header_format=auth_header[:20] if auth_header else None,
            request_id=request.state.request_id,
        )
        raise create_unauthorized_response()

    token = parts[1]

    # Extract user_id from token
    # In development: token could be directly the user_id
    # In production: decode JWT/session token to get user_id
    # For now, treat token as user_id (can be enhanced with JWT decoding)
    user_id = token

    # Validate user_id
    if not validate_user_id(user_id):
        logger.warning(
            "Invalid user_id format",
            user_id=user_id[:10] if user_id else None,
            path=request.url.path,
            method=request.method,
            request_id=request.state.request_id,
        )
        raise create_unauthorized_response()

    # Attach user_id to request state
    request.state.user_id = user_id
    logger.info(
        "User authenticated",
        user_id=user_id,
        path=request.url.path,
        method=request.method,
        request_id=request.state.request_id,
    )

    # Continue to next middleware/endpoint
    response = await call_next(request)
    return response


def create_unauthorized_response():
    """Create 401 Unauthorized JSON response
    
    Raises HTTPException instead of returning it, so that FastAPI's exception
    handler can properly format the response with correct headers.
    """
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(request: Request) -> str:
    """
    FastAPI dependency to get authenticated user_id from request.state
    Returns user_id if authenticated, raises 401 otherwise

    Usage:
        @app.get("/protected")
        async def protected_route(user_id: str = Depends(get_current_user)):
            return {"user_id": user_id}
    """
    user_id = getattr(request.state, "user_id", None)

    if not user_id:
        logger.warning(
            "Unauthorized access attempt",
            path=request.url.path,
            method=request.method,
            request_id=getattr(request.state, "request_id", "unknown"),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


__all__ = ["auth_middleware", "get_current_user", "validate_user_id"]
