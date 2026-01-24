"""
User Endpoints for Todo Chatbot

Provides:
- GET /api/users/me - Get current authenticated user
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from ..db import get_db_session as get_db
from ..logging_config import get_logger
from ..models import User

logger = get_logger(__name__)

# JWT configuration (shared with auth.py)
import os
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"

# Router
router = APIRouter(prefix="/api", tags=["users"])


# ============================================================================
# Response Models
# ============================================================================


class UserResponse(BaseModel):
    """User info response"""

    id: str
    email: str
    name: str
    created_at: str


# ============================================================================
# Utility Functions
# ============================================================================


def verify_token(token: str) -> str:
    """Verify a JWT token and return the user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


# ============================================================================
# Endpoints
# ============================================================================


@router.get("/users/me", response_model=UserResponse)
async def get_current_user(
    authorization: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get current authenticated user

    Requires valid JWT token in Authorization header
    Format: Authorization: Bearer <token>
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    token = parts[1]
    user_id = verify_token(token)

    # Get user from database
    statement = select(User).where(User.user_id == user_id)
    user = db.exec(statement).first()

    if not user:
        logger.warning("user_not_found", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    logger.info("get_current_user_success", user_id=user_id)

    return UserResponse(
        id=user.user_id,
        email=user.email,
        name=user.name,
        created_at=user.created_at.isoformat(),
    )
