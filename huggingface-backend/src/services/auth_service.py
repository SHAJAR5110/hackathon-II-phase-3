"""
Authentication Service
Phase II - Todo Full-Stack Web Application

Handles user signup, signin, password hashing, and JWT token generation.
"""

import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Optional
import os
import uuid
from dotenv import load_dotenv

from models import User, SignupRequest, SigninRequest, UserResponse, AuthResponse

# Load environment variables
load_dotenv()

# JWT settings
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_DAYS = int(os.getenv("JWT_EXPIRATION_DAYS", "7"))

if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is not set")


class AuthService:
    """
    Authentication service for user signup, signin, and token management.

    Methods:
        hash_password: Hash a plain-text password using bcrypt
        verify_password: Verify a password against its hash
        create_jwt_token: Generate a JWT token for a user
        signup: Create a new user account
        signin: Authenticate a user and issue a token
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain-text password using bcrypt.

        Args:
            password: Plain-text password

        Returns:
            str: Bcrypt-hashed password

        Security:
            - Uses bcrypt with automatic salt generation (cost factor 12)
            - Hash is computationally expensive (prevents brute-force)
            - Passwords are truncated to 72 bytes (bcrypt limitation)

        Note:
            Bcrypt has a 72-byte password limit. We truncate passwords to ensure
            compatibility. This is a standard practice with bcrypt.
        """
        # Truncate password to 72 bytes (bcrypt limitation)
        # bcrypt operates on bytes, so we encode and truncate
        password_bytes = password.encode('utf-8')[:72]

        # Generate salt and hash password
        # Cost factor 12 provides good security/performance balance
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Return as string for storage in database
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain-text password against its hash.

        Args:
            plain_password: User-provided password
            hashed_password: Stored bcrypt hash (string)

        Returns:
            bool: True if password matches, False otherwise

        Security:
            - Timing-safe comparison (prevents timing attacks)
            - Passwords are truncated to 72 bytes (must match hash_password behavior)

        Note:
            Must apply same 72-byte truncation as hash_password to ensure
            passwords verify correctly.
        """
        # Truncate password to 72 bytes (must match hash_password behavior)
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')

        # bcrypt.checkpw performs timing-safe comparison
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    @staticmethod
    def create_jwt_token(user_id: str, email: str) -> str:
        """
        Generate a JWT token for a user.

        Args:
            user_id: User's unique identifier
            email: User's email address

        Returns:
            str: JWT token string

        Token Payload:
            - sub: User ID (subject)
            - email: User's email
            - iat: Issued at timestamp
            - exp: Expiration timestamp (7 days from issuance)

        Security:
            - Signed with BETTER_AUTH_SECRET (HS256)
            - Fixed 7-day expiry (no automatic refresh in MVP)
        """
        now = datetime.utcnow()
        expiration = now + timedelta(days=JWT_EXPIRATION_DAYS)

        payload = {
            "sub": user_id,
            "email": email,
            "iat": now,
            "exp": expiration
        }

        return jwt.encode(payload, BETTER_AUTH_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
        """
        Retrieve a user by email address.

        Args:
            session: Database session
            email: User's email address

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        statement = select(User).where(User.email == email.lower())
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def signup(
        session: AsyncSession,
        signup_data: SignupRequest
    ) -> AuthResponse:
        """
        Create a new user account and issue a JWT token.

        Args:
            session: Database session
            signup_data: User signup request (email, password, name)

        Returns:
            AuthResponse: User data and JWT token

        Raises:
            ValueError: If email is already registered

        Process:
            1. Check if email already exists (409 Conflict)
            2. Hash password with bcrypt
            3. Generate unique user ID (UUID)
            4. Create user record in database
            5. Generate JWT token (7-day expiry)
            6. Return user data and token

        Security:
            - Password is hashed before storage (never stored in plaintext)
            - Email is normalized to lowercase
            - User ID is a UUID v4 (unpredictable)
        """
        print(f"[AUTH_SERVICE] Signup request received for email: {signup_data.email}")

        # Check if email already exists
        print(f"[AUTH_SERVICE] Checking if email already exists: {signup_data.email}")
        existing_user = await AuthService.get_user_by_email(session, signup_data.email)
        if existing_user:
            print(f"[AUTH_SERVICE] Email already registered: {signup_data.email}")
            raise ValueError("Email already registered")

        print(f"[AUTH_SERVICE] Email not found, proceeding with signup")

        # Hash password
        print(f"[AUTH_SERVICE] Hashing password for user: {signup_data.email}")
        password_hash = AuthService.hash_password(signup_data.password)
        print(f"[AUTH_SERVICE] Password hashed successfully (length: {len(password_hash)})")

        # Generate user ID
        user_id = str(uuid.uuid4())
        print(f"[AUTH_SERVICE] Generated user ID: {user_id}")

        # Create user
        print(f"[AUTH_SERVICE] Creating user record in database")
        new_user = User(
            id=user_id,
            email=signup_data.email.lower(),
            password_hash=password_hash,
            name=signup_data.name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        try:
            session.add(new_user)
            print(f"[AUTH_SERVICE] User added to session, committing transaction")
            await session.commit()
            print(f"[AUTH_SERVICE] Transaction committed successfully")
            await session.refresh(new_user)
            print(f"[AUTH_SERVICE] User refreshed from database")
        except Exception as e:
            print(f"[AUTH_SERVICE] ERROR during database operation: {e}")
            raise

        # Generate JWT token
        print(f"[AUTH_SERVICE] Generating JWT token for user: {new_user.id}")
        token = AuthService.create_jwt_token(new_user.id, new_user.email)
        print(f"[AUTH_SERVICE] JWT token generated successfully (length: {len(token)})")

        # Return response
        user_response = UserResponse(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            created_at=new_user.created_at
        )

        auth_response = AuthResponse(
            user=user_response,
            token=token,
            expires_in=JWT_EXPIRATION_DAYS * 24 * 60 * 60  # 7 days in seconds
        )

        print(f"[AUTH_SERVICE] Signup successful for user: {new_user.email}")
        return auth_response

    @staticmethod
    async def signin(
        session: AsyncSession,
        signin_data: SigninRequest
    ) -> AuthResponse:
        """
        Authenticate a user and issue a JWT token.

        Args:
            session: Database session
            signin_data: User signin request (email, password)

        Returns:
            AuthResponse: User data and JWT token

        Raises:
            ValueError: If email doesn't exist or password is incorrect

        Process:
            1. Retrieve user by email
            2. Verify password against stored hash
            3. Generate JWT token (7-day expiry)
            4. Return user data and token

        Security:
            - Generic error message (don't reveal if email exists)
            - Timing-safe password comparison
            - Password hash never exposed in response
        """
        print(f"[AUTH_SERVICE] Signin request received for email: {signin_data.email}")

        # Retrieve user
        print(f"[AUTH_SERVICE] Retrieving user by email: {signin_data.email}")
        user = await AuthService.get_user_by_email(session, signin_data.email)

        if not user:
            print(f"[AUTH_SERVICE] User not found for email: {signin_data.email}")
            raise ValueError("Invalid email or password")

        print(f"[AUTH_SERVICE] User found: {user.id}, verifying password")

        # Verify credentials
        password_valid = AuthService.verify_password(signin_data.password, user.password_hash)
        print(f"[AUTH_SERVICE] Password verification result: {password_valid}")

        if not password_valid:
            print(f"[AUTH_SERVICE] Password verification failed for user: {signin_data.email}")
            raise ValueError("Invalid email or password")

        print(f"[AUTH_SERVICE] Password verified successfully")

        # Generate JWT token
        print(f"[AUTH_SERVICE] Generating JWT token for user: {user.id}")
        token = AuthService.create_jwt_token(user.id, user.email)
        print(f"[AUTH_SERVICE] JWT token generated successfully (length: {len(token)})")

        # Return response
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at
        )

        auth_response = AuthResponse(
            user=user_response,
            token=token,
            expires_in=JWT_EXPIRATION_DAYS * 24 * 60 * 60  # 7 days in seconds
        )

        print(f"[AUTH_SERVICE] Signin successful for user: {user.email}")
        return auth_response
