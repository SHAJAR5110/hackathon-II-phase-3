"""
Authentication Endpoints for Todo Chatbot

Provides:
- POST /api/auth/signin - User login
- POST /api/auth/signup - User registration
- POST /api/auth/logout - User logout
- GET /api/users/me - Get current user
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from ..db import get_db_session as get_db
from ..logging_config import get_logger
from ..models import User

logger = get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Router
router = APIRouter(prefix="/api/auth", tags=["auth"])


# ============================================================================
# Request/Response Models
# ============================================================================


class SigninRequest(BaseModel):
    """Login request"""

    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    """Registration request"""

    email: EmailStr
    password: str
    name: str


class AuthResponse(BaseModel):
    """Authentication response"""

    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    """User info response"""

    id: str
    email: str
    name: str
    created_at: str


# ============================================================================
# Utility Functions
# ============================================================================


def hash_password(password: str) -> str:
    """Hash a password using bcrypt

    Bcrypt has a 72-byte limit, so we truncate passwords to 72 bytes
    to prevent "password too long" errors while maintaining security
    """
    # Truncate to 72 bytes (bcrypt limit)
    truncated = password.encode()[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash

    Must truncate to same 72-byte limit as hash_password for consistency
    """
    # Truncate to 72 bytes (same as hash_password)
    truncated = plain_password.encode()[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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
# Dependency
# ============================================================================


async def get_current_user_id(token: str = None) -> str:
    """
    Dependency to get current user ID from Authorization header
    Can be used in routes: current_user: str = Depends(get_current_user_id)
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return verify_token(token)


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/signin", response_model=AuthResponse)
async def signin(request: SigninRequest, db: Session = Depends(get_db)):
    """
    User login endpoint

    Returns JWT token and user info on success
    """
    logger.info("signin_attempt", email=request.email)

    # Find user by email
    statement = select(User).where(User.email == request.email)
    user = db.exec(statement).first()

    if not user or not verify_password(request.password, user.hashed_password):
        logger.warning(
            "signin_failed", email=request.email, reason="invalid_credentials"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.user_id})

    logger.info("signin_success", user_id=user.user_id)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.user_id,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat(),
        },
    )


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    User registration endpoint

    Creates a new user account
    """
    logger.info("signup_attempt", email=request.email)

    # Check if user already exists
    statement = select(User).where(User.email == request.email)
    existing_user = db.exec(statement).first()

    if existing_user:
        logger.warning("signup_failed", email=request.email, reason="email_exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user_id = request.email.split("@")[0]  # Simple user_id from email
    user = User(
        user_id=user_id,
        email=request.email,
        name=request.name,
        hashed_password=hash_password(request.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("signup_success", user_id=user.user_id)

    return {
        "message": "User registered successfully",
        "user_id": user.user_id,
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(authorization: Optional[str] = None):
    """
    User logout endpoint

    Note: JWT tokens are stateless, so logout just requires
    the client to delete the token. This endpoint is here for
    logging and potential token blacklisting in the future.
    """
    if authorization:
        try:
            token = authorization.replace("Bearer ", "")
            user_id = verify_token(token)
            logger.info("logout_success", user_id=user_id)
        except HTTPException:
            logger.warning("logout_failed", reason="invalid_token")

    return {"message": "Logged out successfully"}


@router.get("/users/me", response_model=UserResponse)
async def get_current_user(
    authorization: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get current authenticated user

    Requires valid JWT token in Authorization header
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

    return UserResponse(
        id=user.user_id,
        email=user.email,
        name=user.name,
        created_at=user.created_at.isoformat(),
    )
