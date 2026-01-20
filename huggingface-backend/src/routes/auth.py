"""
Authentication Routes
Phase II - Todo Full-Stack Web Application

Handles user signup, signin, and logout endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from db import get_session
from models import SignupRequest, SigninRequest, AuthResponse, ErrorResponse
from services.auth_service import AuthService

# Create router for authentication endpoints
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid input (validation error)"},
        409: {"model": ErrorResponse, "description": "Email already registered"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def signup(
    signup_data: SignupRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new user account.

    **Request Body:**
    - email: Valid email address
    - password: Minimum 8 characters, must contain uppercase, lowercase, and number
    - name: User's display name (1-100 characters)

    **Response:**
    - 201: User created successfully with JWT token
    - 400: Invalid input (email format, weak password, empty name)
    - 409: Email already registered
    - 500: Internal server error

    **Process:**
    1. Validate input (email format, password strength, name)
    2. Check if email already exists
    3. Hash password with bcrypt
    4. Create user record in database
    5. Generate JWT token (7-day expiry)
    6. Return user data and token

    **Security:**
    - Password is hashed with bcrypt before storage
    - JWT token contains user_id, email, iat, exp claims
    - Token expires after 7 days (no automatic refresh)

    **Example:**
    ```json
    {
        "email": "user@example.com",
        "password": "SecurePass123",
        "name": "John Doe"
    }
    ```

    **Response:**
    ```json
    {
        "user": {
            "id": "uuid-here",
            "email": "user@example.com",
            "name": "John Doe",
            "created_at": "2024-01-04T12:00:00Z"
        },
        "token": "jwt-token-here",
        "expires_in": 604800
    }
    ```
    """
    print(f"[AUTH_ROUTE] POST /auth/signup - Email: {signup_data.email}, Name: {signup_data.name}")

    try:
        # Call AuthService to create user
        print(f"[AUTH_ROUTE] Calling AuthService.signup()")
        auth_response = await AuthService.signup(session, signup_data)
        print(f"[AUTH_ROUTE] Signup successful, returning 201")
        return auth_response

    except ValueError as e:
        error_msg = str(e)
        print(f"[AUTH_ROUTE] ValueError caught: {error_msg}")
        # Email already registered
        if "already registered" in error_msg.lower():
            print(f"[AUTH_ROUTE] Returning 409 Conflict")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg
            )
        # Other validation errors
        print(f"[AUTH_ROUTE] Returning 400 Bad Request")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    except Exception as e:
        # Unexpected server error
        print(f"[AUTH_ROUTE] Unexpected error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/signin",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User authenticated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid input (validation error)"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def signin(
    signin_data: SigninRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Authenticate a user and issue a JWT token.

    **Request Body:**
    - email: User's email address
    - password: User's password

    **Response:**
    - 200: User authenticated successfully with JWT token
    - 400: Invalid input (email format, empty password)
    - 401: Invalid email or password
    - 500: Internal server error

    **Process:**
    1. Validate input (email format, password not empty)
    2. Retrieve user by email
    3. Verify password against stored bcrypt hash
    4. Generate JWT token (7-day expiry)
    5. Return user data and token

    **Security:**
    - Generic error message (doesn't reveal if email exists)
    - Timing-safe password comparison
    - Password hash never exposed in response
    - JWT token contains user_id, email, iat, exp claims

    **Example:**
    ```json
    {
        "email": "user@example.com",
        "password": "SecurePass123"
    }
    ```

    **Response:**
    ```json
    {
        "user": {
            "id": "uuid-here",
            "email": "user@example.com",
            "name": "John Doe",
            "created_at": "2024-01-04T12:00:00Z"
        },
        "token": "jwt-token-here",
        "expires_in": 604800
    }
    ```
    """
    print(f"[AUTH_ROUTE] POST /auth/signin - Email: {signin_data.email}")

    try:
        # Call AuthService to authenticate user
        print(f"[AUTH_ROUTE] Calling AuthService.signin()")
        auth_response = await AuthService.signin(session, signin_data)
        print(f"[AUTH_ROUTE] Signin successful, returning 200")
        return auth_response

    except ValueError as e:
        error_msg = str(e)
        print(f"[AUTH_ROUTE] ValueError caught: {error_msg}")
        # Invalid credentials
        if "invalid email or password" in error_msg.lower():
            print(f"[AUTH_ROUTE] Returning 401 Unauthorized")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )
        # Other validation errors
        print(f"[AUTH_ROUTE] Returning 400 Bad Request")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    except Exception as e:
        # Unexpected server error
        print(f"[AUTH_ROUTE] Unexpected error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User logged out successfully"},
    }
)
async def logout():
    """
    Log out a user (client-side token removal).

    **Response:**
    - 200: Logout successful (client should clear token)

    **Process:**
    1. Return success message
    2. Client is responsible for removing JWT token from storage

    **Note:**
    - In MVP, logout is client-side only (clear token from cookie/localStorage)
    - No server-side token revocation/blacklist in MVP
    - Token remains valid until expiry (7 days from issuance)
    - Phase III will add token revocation for enhanced security

    **Client Implementation:**
    - Remove JWT token from HTTP-only cookie
    - Clear user data from localStorage
    - Redirect to signin page
    """
    return {"message": "Logout successful. Client should clear token."}
