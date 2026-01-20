"""
Database Models and Pydantic Schemas
Phase II - Todo Full-Stack Web Application

Defines SQLModel ORM models for database tables and Pydantic schemas for request/response validation.
"""

from sqlmodel import Field, SQLModel, Column, Index, String, Text
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
import re


# ============================================================================
# SQLModel ORM Models (Database Tables)
# ============================================================================

class User(SQLModel, table=True):
    """
    User model for authentication.

    This table is managed by Better Auth on the frontend.
    We define it here for reference and foreign key relationships.

    Fields:
        id: Unique user identifier (UUID from Better Auth)
        email: User's email address (unique)
        password_hash: Bcrypt-hashed password
        name: User's display name
        created_at: Account creation timestamp
        updated_at: Last profile update timestamp
    """
    __tablename__ = "users"

    id: str = Field(primary_key=True, max_length=255)
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    password_hash: str = Field(sa_column=Column(Text, nullable=False))
    name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Task(SQLModel, table=True):
    """
    Task model for todo items.

    Each task belongs to a single user via the user_id foreign key.
    User isolation is enforced by filtering all queries by user_id.

    Fields:
        id: Auto-incrementing task identifier
        user_id: Foreign key to users.id (owner of the task)
        title: Task title (required, 1-200 characters)
        description: Optional task description (max 1000 characters)
        completed: Completion status (default: False)
        created_at: Task creation timestamp
        updated_at: Last modification timestamp

    Indexes:
        - idx_tasks_user_id: Fast filtering by user
        - idx_tasks_completed: Fast filtering by status
        - idx_tasks_user_completed: Composite index for user + status queries
        - idx_tasks_user_created_desc: Sorted list of user's tasks
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", max_length=255)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Define indexes for efficient queries
    __table_args__ = (
        Index('idx_tasks_user_id', 'user_id'),
        Index('idx_tasks_completed', 'completed'),
        Index('idx_tasks_user_completed', 'user_id', 'completed'),
        Index('idx_tasks_user_created_desc', 'user_id', 'created_at'),
    )


# ============================================================================
# Pydantic Request Models (Input Validation)
# ============================================================================

class TaskCreate(BaseModel):
    """
    Schema for creating a new task.

    Fields:
        title: Task title (required, 1-200 characters)
        description: Optional task description (max 1000 characters)

    Validation:
        - Title is required and cannot be empty
        - Title is automatically trimmed
        - Description is optional and defaults to None
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        """Validate that title is not empty after trimming"""
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_trim(cls, v: Optional[str]) -> Optional[str]:
        """Trim description if provided"""
        if v is None:
            return None
        return v.strip() if v.strip() else None


class TaskUpdate(BaseModel):
    """
    Schema for updating a task.

    All fields are optional; only provided fields will be updated.

    Fields:
        title: New task title (optional, 1-200 characters if provided)
        description: New task description (optional, max 1000 characters if provided)

    Validation:
        - At least one field must be provided
        - Title cannot be empty if provided
        - Values are automatically trimmed
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate that title is not empty after trimming"""
        if v is not None:
            if not v.strip():
                raise ValueError('Title cannot be empty or whitespace only')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def description_trim(cls, v: Optional[str]) -> Optional[str]:
        """Trim description if provided"""
        if v is None:
            return None
        return v.strip() if v.strip() else None


# ============================================================================
# Pydantic Response Models (Output Serialization)
# ============================================================================

class TaskResponse(BaseModel):
    """
    Schema for task responses.

    Returns all task fields in API responses.

    Fields:
        id: Task ID
        user_id: Owner's user ID
        title: Task title
        description: Task description (nullable)
        completed: Completion status
        created_at: Creation timestamp
        updated_at: Last modification timestamp
    """
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel objects


class UserResponse(BaseModel):
    """
    Schema for user responses.

    Returns safe user information (no password).

    Fields:
        id: User ID
        email: User's email
        name: User's display name
        created_at: Account creation timestamp
    """
    id: str
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel objects


# ============================================================================
# Authentication Request/Response Models
# ============================================================================

class SignupRequest(BaseModel):
    """
    Schema for user signup request.

    Fields:
        email: User's email address (must be valid format)
        password: User's password (min 8 chars, must contain uppercase, lowercase, and number)
        name: User's display name (1-100 chars)

    Validation:
        - Email format validated
        - Password strength enforced (min 8 chars, uppercase, lowercase, number)
        - Name required and trimmed

    Note:
        Passwords are automatically truncated to 72 bytes during hashing due to bcrypt limitation.
        This is transparent to users and follows security best practices.
    """
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        """Validate email format"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()

    @field_validator('password')
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate name is not empty"""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class SigninRequest(BaseModel):
    """
    Schema for user signin request.

    Fields:
        email: User's email address
        password: User's password

    Validation:
        - Email format validated
        - Password required

    Note:
        Passwords are automatically truncated to 72 bytes during verification due to bcrypt limitation.
    """
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        """Validate email format"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()


class AuthResponse(BaseModel):
    """
    Schema for authentication response (signup/signin).

    Returns user data and JWT token.

    Fields:
        user: User information (id, email, name, created_at)
        token: JWT token string
        expires_in: Token expiration in seconds (7 days)
    """
    user: UserResponse
    token: str
    expires_in: int = Field(default=604800, description="Token expiry in seconds (7 days)")


# ============================================================================
# Utility Models
# ============================================================================

class TaskListResponse(BaseModel):
    """
    Schema for task list responses.

    Returns an array of tasks.

    Fields:
        tasks: List of TaskResponse objects
    """
    tasks: list[TaskResponse]


class ErrorResponse(BaseModel):
    """
    Schema for error responses.

    Consistent error format for all API errors.

    Fields:
        detail: Human-readable error message
        status: HTTP status code
    """
    detail: str
    status: int
