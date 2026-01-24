"""
MCP Tool: complete_task
Marks a task as completed
"""

from sqlalchemy.orm import Session

from ...db import SessionLocal
from ...logging_config import get_logger
from ...repositories import TaskRepository

logger = get_logger(__name__)


def complete_task(
    user_id: str,
    task_id: int,
) -> dict:
    """
    Mark a task as completed

    Parameters:
        user_id (str, required): The user ID
        task_id (int, required): The task ID to complete

    Returns:
        {
            "task_id": int,
            "status": "completed",
            "title": str
        }

    Raises:
        ValueError: If parameters are invalid
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        logger.warning("complete_task_invalid_user_id", user_id=user_id)
        return {
            "error": "invalid_user_id",
            "message": "User ID is required and must be a string",
        }

    if not isinstance(task_id, int) or task_id <= 0:
        logger.warning(
            "complete_task_invalid_task_id", user_id=user_id, task_id=task_id
        )
        return {
            "error": "invalid_task_id",
            "message": "Task ID must be a positive integer",
        }

    db: Session = SessionLocal()
    try:
        # Read task to verify ownership
        task = TaskRepository.read(db, user_id, task_id)

        if not task:
            logger.warning("complete_task_not_found", user_id=user_id, task_id=task_id)
            return {"error": "task_not_found", "message": f"Task {task_id} not found"}

        # Update task to mark as completed
        updated_task = TaskRepository.update(
            db=db, user_id=user_id, task_id=task_id, completed=True
        )

        logger.info(
            "complete_task_success",
            user_id=user_id,
            task_id=task_id,
            title=updated_task.title,
        )

        return {
            "task_id": updated_task.id,
            "status": "completed",
            "title": updated_task.title,
        }

    except Exception as e:
        logger.error(
            "complete_task_failed", user_id=user_id, task_id=task_id, error=str(e)
        )
        return {"error": "task_update_failed", "message": "Failed to complete task"}

    finally:
        db.close()
