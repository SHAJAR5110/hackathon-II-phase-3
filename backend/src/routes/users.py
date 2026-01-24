"""
User Endpoints for Todo Chatbot

Provides:
- GET /api/users/me - Get current authenticated user
"""

from pydantic import BaseModel
from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException, status, Request

from ..db import get_db_session as get_db
from ..logging_config import get_logger
from ..models import User
from ..middleware.auth import get_current_user

logger = get_logger(__name__)

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
# Endpoints
# ============================================================================


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_endpoint(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current authenticated user

    Auth is handled by middleware - just get user from database using validated user_id.
    """
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
