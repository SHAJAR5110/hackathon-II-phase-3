"""
MCP Tool: add_task
Creates a new task for the user
"""

from typing import Optional

from sqlalchemy.orm import Session

from ...db import SessionLocal
from ...logging_config import get_logger
from ...repositories import TaskRepository

logger = get_logger(__name__)


def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
) -> dict:
    """
    Create a new task

    Parameters:
        user_id (str, required): The user ID
        title (str, required): Task title (max 1000 chars)
        description (str, optional): Task description (max 1000 chars)

    Returns:
        {
            "task_id": int,
            "status": "created",
            "title": str
        }

    Raises:
        ValueError: If required parameters are invalid
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        logger.warning("add_task_invalid_user_id", user_id=user_id)
        return {
            "error": "invalid_user_id",
            "message": "User ID is required and must be a string",
        }

    if not title or not isinstance(title, str):
        logger.warning("add_task_invalid_title", user_id=user_id, title=title)
        return {
            "error": "invalid_title",
            "message": "Title is required and must be a string",
        }

    if len(title) > 1000:
        logger.warning(
            "add_task_title_too_long", user_id=user_id, title_length=len(title)
        )
        return {
            "error": "title_too_long",
            "message": "Title must be 1000 characters or less",
        }

    if description and len(description) > 1000:
        logger.warning(
            "add_task_description_too_long",
            user_id=user_id,
            description_length=len(description),
        )
        return {
            "error": "description_too_long",
            "message": "Description must be 1000 characters or less",
        }

    db: Session = SessionLocal()
    try:
        # Create task in database
        task = TaskRepository.create(
            db=db, user_id=user_id, title=title, description=description
        )

        logger.info("add_task_success", user_id=user_id, task_id=task.id, title=title)

        return {"task_id": task.id, "status": "created", "title": task.title}

    except Exception as e:
        logger.error("add_task_failed", user_id=user_id, title=title, error=str(e))
        return {"error": "task_creation_failed", "message": "Failed to create task"}

    finally:
        db.close()
