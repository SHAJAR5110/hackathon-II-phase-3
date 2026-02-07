"""
User API Routes
Phase II - Todo Full-Stack Web Application

Implements user profile endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ..db import get_session
from ..middleware.auth import get_current_user_id
from ..models import UserResponse
from sqlmodel import select
from ..models import User

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get the current authenticated user's information.

    Security:
        - Requires valid JWT token
        - Returns only the authenticated user's data

    Returns:
        UserResponse: Current user's profile information

    Raises:
        401: If token is invalid or missing
        404: If user not found (token is valid but user was deleted)
    """
    # Fetch user from database
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
