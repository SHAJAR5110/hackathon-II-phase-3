"""
MCP Tool: delete_task
Removes a task from the database
"""

from sqlalchemy.orm import Session

from ...db import SessionLocal
from ...logging_config import get_logger
from ...repositories import TaskRepository

logger = get_logger(__name__)


def delete_task(
    user_id: str,
    task_id: int,
) -> dict:
    """
    Delete a task

    Parameters:
        user_id (str, required): The user ID
        task_id (int, required): The task ID to delete

    Returns:
        {
            "task_id": int,
            "status": "deleted",
            "title": str
        }

    Raises:
        ValueError: If parameters are invalid
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        logger.warning("delete_task_invalid_user_id", user_id=user_id)
        return {
            "error": "invalid_user_id",
            "message": "User ID is required and must be a string",
        }

    if not isinstance(task_id, int) or task_id <= 0:
        logger.warning("delete_task_invalid_task_id", user_id=user_id, task_id=task_id)
        return {
            "error": "invalid_task_id",
            "message": "Task ID must be a positive integer",
        }

    db: Session = SessionLocal()
    try:
        # Read task to verify ownership and get details before deletion
        task = TaskRepository.read(db, user_id, task_id)

        if not task:
            logger.warning("delete_task_not_found", user_id=user_id, task_id=task_id)
            return {"error": "task_not_found", "message": f"Task {task_id} not found"}

        # Store task info before deletion
        task_title = task.title
        task_id_val = task.id

        # Delete task
        success = TaskRepository.delete(db, user_id, task_id)

        if not success:
            logger.warning(
                "delete_task_failed_to_delete", user_id=user_id, task_id=task_id
            )
            return {
                "error": "task_deletion_failed",
                "message": f"Failed to delete task {task_id}",
            }

        logger.info(
            "delete_task_success", user_id=user_id, task_id=task_id, title=task_title
        )

        return {"task_id": task_id_val, "status": "deleted", "title": task_title}

    except Exception as e:
        logger.error(
            "delete_task_failed", user_id=user_id, task_id=task_id, error=str(e)
        )
        return {"error": "task_deletion_failed", "message": "Failed to delete task"}

    finally:
        db.close()
