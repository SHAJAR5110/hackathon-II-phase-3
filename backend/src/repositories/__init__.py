"""
Data access layer - Repository pattern
All database operations go through repositories
"""

from typing import List, Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from ..logging_config import get_logger
from ..models import Conversation, Message, Task

logger = get_logger(__name__)


class TaskRepository:
    """Repository for Task operations"""

    @staticmethod
    def create(
        db: Session, user_id: str, title: str, description: Optional[str] = None
    ) -> Task:
        """Create a new task"""
        try:
            task = Task(user_id=user_id, title=title, description=description)
            db.add(task)
            db.commit()
            db.refresh(task)
            logger.info("task_created", user_id=user_id, task_id=task.id, title=title)
            return task
        except Exception as e:
            db.rollback()
            logger.error("task_create_failed", user_id=user_id, error=str(e))
            raise

    @staticmethod
    def read(db: Session, user_id: str, task_id: int) -> Optional[Task]:
        """Read a task by ID (must belong to user)"""
        return (
            db.query(Task)
            .filter(and_(Task.id == task_id, Task.user_id == user_id))
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        user_id: str,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> Optional[Task]:
        """Update a task (must belong to user)"""
        try:
            task = TaskRepository.read(db, user_id, task_id)
            if not task:
                return None

            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if completed is not None:
                task.completed = completed

            db.add(task)
            db.commit()
            db.refresh(task)
            logger.info("task_updated", user_id=user_id, task_id=task_id)
            return task
        except Exception as e:
            db.rollback()
            logger.error(
                "task_update_failed", user_id=user_id, task_id=task_id, error=str(e)
            )
            raise

    @staticmethod
    def delete(db: Session, user_id: str, task_id: int) -> bool:
        """Delete a task (must belong to user)"""
        try:
            task = TaskRepository.read(db, user_id, task_id)
            if not task:
                return False

            db.delete(task)
            db.commit()
            logger.info("task_deleted", user_id=user_id, task_id=task_id)
            return True
        except Exception as e:
            db.rollback()
            logger.error(
                "task_delete_failed", user_id=user_id, task_id=task_id, error=str(e)
            )
            raise

    @staticmethod
    def list_by_user(db: Session, user_id: str, status: str = "all") -> List[Task]:
        """List tasks for user, optionally filtered by status"""
        query = db.query(Task).filter(Task.user_id == user_id)

        if status == "pending":
            query = query.filter(Task.completed == False)
        elif status == "completed":
            query = query.filter(Task.completed == True)

        return query.order_by(desc(Task.created_at)).all()

    @staticmethod
    def list_by_conversation(
        db: Session, user_id: str, conversation_id: int
    ) -> List[Task]:
        """List tasks (for a user) - contextual to conversation if needed"""
        return TaskRepository.list_by_user(db, user_id, status="all")


class ConversationRepository:
    """Repository for Conversation operations"""

    @staticmethod
    def create(db: Session, user_id: str) -> Conversation:
        """Create a new conversation"""
        try:
            conversation = Conversation(user_id=user_id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            logger.info(
                "conversation_created", user_id=user_id, conversation_id=conversation.id
            )
            return conversation
        except Exception as e:
            db.rollback()
            logger.error("conversation_create_failed", user_id=user_id, error=str(e))
            raise

    @staticmethod
    def read(db: Session, user_id: str, conversation_id: int) -> Optional[Conversation]:
        """Read a conversation (must belong to user)"""
        return (
            db.query(Conversation)
            .filter(
                and_(
                    Conversation.id == conversation_id, Conversation.user_id == user_id
                )
            )
            .first()
        )

    @staticmethod
    def list_by_user(
        db: Session, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Conversation]:
        """List conversations for user"""
        return (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .offset(offset)
            .limit(limit)
            .all()
        )


class MessageRepository:
    """Repository for Message operations"""

    @staticmethod
    def create(
        db: Session, user_id: str, conversation_id: int, role: str, content: str
    ) -> Message:
        """Create a new message"""
        try:
            message = Message(
                user_id=user_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            logger.info(
                "message_created",
                user_id=user_id,
                conversation_id=conversation_id,
                message_id=message.id,
                role=role,
            )
            return message
        except Exception as e:
            db.rollback()
            logger.error(
                "message_create_failed",
                user_id=user_id,
                conversation_id=conversation_id,
                error=str(e),
            )
            raise

    @staticmethod
    def list_by_conversation(
        db: Session,
        conversation_id: int,
        limit: int = 100,
        offset: int = 0,
        user_id: str = None,
    ) -> List[Message]:
        """List messages in a conversation (optionally filtered by user_id for security)"""
        query = db.query(Message).filter(Message.conversation_id == conversation_id)

        # If user_id is provided, add user_id filter for extra security
        if user_id:
            query = query.filter(Message.user_id == user_id)

        return query.order_by(Message.created_at).offset(offset).limit(limit).all()

    @staticmethod
    def count_by_conversation(db: Session, conversation_id: int) -> int:
        """Count messages in a conversation"""
        return (
            db.query(Message).filter(Message.conversation_id == conversation_id).count()
        )


__all__ = ["TaskRepository", "ConversationRepository", "MessageRepository"]
