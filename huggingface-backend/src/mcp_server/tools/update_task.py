"""
MCP Tool: update_task
Modifies a task's title or description
"""

from typing import Optional

from sqlalchemy.orm import Session

from ...db import SessionLocal
from ...logging_config import get_logger
from ...repositories import TaskRepository

logger = get_logger(__name__)


def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """
    Update a task's title or description

    Parameters:
        user_id (str, required): The user ID
        task_id (int, required): The task ID to update
        title (str, optional): New task title (max 1000 chars)
        description (str, optional): New task description (max 1000 chars)

    Returns:
        {
            "task_id": int,
            "status": "updated",
            "title": str
        }

    Raises:
        ValueError: If parameters are invalid
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        logger.warning("update_task_invalid_user_id", user_id=user_id)
        return {
            "error": "invalid_user_id",
            "message": "User ID is required and must be a string",
        }

    if not isinstance(task_id, int) or task_id <= 0:
        logger.warning("update_task_invalid_task_id", user_id=user_id, task_id=task_id)
        return {
            "error": "invalid_task_id",
            "message": "Task ID must be a positive integer",
        }

    # Require at least one of title or description
    if title is None and description is None:
        logger.warning("update_task_no_updates", user_id=user_id, task_id=task_id)
        return {
            "error": "no_updates_provided",
            "message": "At least one of title or description must be provided",
        }

    # Validate title if provided
    if title is not None:
        if not isinstance(title, str):
            logger.warning(
                "update_task_invalid_title",
                user_id=user_id,
                task_id=task_id,
                title=title,
            )
            return {"error": "invalid_title", "message": "Title must be a string"}

        if len(title) > 1000:
            logger.warning(
                "update_task_title_too_long",
                user_id=user_id,
                task_id=task_id,
                title_length=len(title),
            )
            return {
                "error": "title_too_long",
                "message": "Title must be 1000 characters or less",
            }

    # Validate description if provided
    if description is not None:
        if not isinstance(description, str):
            logger.warning(
                "update_task_invalid_description",
                user_id=user_id,
                task_id=task_id,
                description=description,
            )
            return {
                "error": "invalid_description",
                "message": "Description must be a string",
            }

        if len(description) > 1000:
            logger.warning(
                "update_task_description_too_long",
                user_id=user_id,
                task_id=task_id,
                description_length=len(description),
            )
            return {
                "error": "description_too_long",
                "message": "Description must be 1000 characters or less",
            }

    db: Session = SessionLocal()
    try:
        # Read task to verify ownership
        task = TaskRepository.read(db, user_id, task_id)

        if not task:
            logger.warning("update_task_not_found", user_id=user_id, task_id=task_id)
            return {"error": "task_not_found", "message": f"Task {task_id} not found"}

        # Update task
        updated_task = TaskRepository.update(
            db=db,
            user_id=user_id,
            task_id=task_id,
            title=title,
            description=description,
        )

        logger.info(
            "update_task_success",
            user_id=user_id,
            task_id=task_id,
            title=updated_task.title,
        )

        return {
            "task_id": updated_task.id,
            "status": "updated",
            "title": updated_task.title,
        }

    except Exception as e:
        logger.error(
            "update_task_failed", user_id=user_id, task_id=task_id, error=str(e)
        )
        return {"error": "task_update_failed", "message": "Failed to update task"}

    finally:
        db.close()
