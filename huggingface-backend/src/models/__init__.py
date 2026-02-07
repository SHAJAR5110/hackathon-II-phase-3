"""
SQLModel ORM models for Todo Chatbot
- User: Authenticated user
- Task: Todo item
- Conversation: Chat session
- Message: Individual message in conversation
- Pydantic schemas for request/response validation
"""

import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field as PydanticField, field_validator
from sqlalchemy import Column, DateTime, Text, Index, func
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """User model - authenticated user"""
    __tablename__ = "users"

    id: str = Field(primary_key=True, index=True, max_length=255)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime, onupdate=func.now())
    )

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")
    messages: List["Message"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    """Task model - todo item"""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=1000, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime, onupdate=func.now())
    )

    # Relationships
    user: Optional[User] = Relationship(back_populates="tasks")


class Conversation(SQLModel, table=True):
    """Conversation model - chat session"""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime, onupdate=func.now())
    )

    # Relationships
    user: Optional[User] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation", cascade_delete=True
    )


class Message(SQLModel, table=True):
    """Message model - individual message in conversation"""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20, index=True)  # "user" or "assistant"
    content: str = Field()  # Message text
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, server_default=func.now()),
    )

    # Relationships
    user: Optional[User] = Relationship(back_populates="messages")
    conversation: Optional[Conversation] = Relationship(back_populates="messages")


# ============================================================================
# Pydantic Request/Response Models
# ============================================================================

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = PydanticField(..., min_length=1, max_length=200)
    description: Optional[str] = PydanticField(None, max_length=1000)

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_trim(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return v.strip() if v.strip() else None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = PydanticField(None, min_length=1, max_length=200)
    description: Optional[str] = PydanticField(None, max_length=1000)

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError('Title cannot be empty or whitespace only')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def description_trim(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return v.strip() if v.strip() else None


class TaskResponse(BaseModel):
    """Schema for task responses."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for task list responses."""
    tasks: list[TaskResponse]


class UserResponse(BaseModel):
    """Schema for user responses."""
    id: str
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class SignupRequest(BaseModel):
    """Schema for user signup request."""
    email: str = PydanticField(..., min_length=3, max_length=255)
    password: str = PydanticField(..., min_length=8, max_length=128)
    name: str = PydanticField(..., min_length=1, max_length=100)

    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()

    @field_validator('password')
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
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
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class SigninRequest(BaseModel):
    """Schema for user signin request."""
    email: str = PydanticField(..., min_length=3, max_length=255)
    password: str = PydanticField(..., min_length=1, max_length=128)

    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()


class AuthResponse(BaseModel):
    """Schema for authentication response."""
    user: UserResponse
    token: str
    expires_in: int = PydanticField(default=604800, description="Token expiry in seconds (7 days)")


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    status: int


# Export all models
__all__ = [
    "User", "Task", "Conversation", "Message",
    "TaskCreate", "TaskUpdate", "TaskResponse", "TaskListResponse",
    "UserResponse", "SignupRequest", "SigninRequest", "AuthResponse", "ErrorResponse",
]
