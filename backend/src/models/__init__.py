"""
SQLModel ORM models for Todo Chatbot
- User: Authenticated user
- Task: Todo item
- Conversation: Chat session
- Message: Individual message in conversation
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """User model - authenticated user"""

    user_id: str = Field(primary_key=True, index=True, max_length=255)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    hashed_password: str = Field(max_length=255)
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

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.user_id", index=True)
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

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.user_id", index=True)
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

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.user_id", index=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    role: str = Field(max_length=20, index=True)  # "user" or "assistant"
    content: str = Field()  # Message text
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, server_default=func.now()),
    )

    # Relationships
    user: Optional[User] = Relationship(back_populates="messages")
    conversation: Optional[Conversation] = Relationship(back_populates="messages")


# Export all models
__all__ = ["User", "Task", "Conversation", "Message"]
