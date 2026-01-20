"""
MCP Tool: list_tasks
Retrieves tasks for a user, optionally filtered by status
"""

from typing import List

from sqlalchemy.orm import Session

from ...db import SessionLocal
from ...logging_config import get_logger
from ...repositories import TaskRepository

logger = get_logger(__name__)


def list_tasks(
    user_id: str,
    status: str = "all",
) -> dict:
    """
    Retrieve tasks for user, optionally filtered by status

    Parameters:
        user_id (str, required): The user ID
        status (str, optional): Filter by status - "all" (default), "pending", "completed"

    Returns:
        {
            "tasks": [
                {
                    "id": int,
                    "title": str,
                    "description": str (nullable),
                    "completed": bool,
                    "created_at": str (ISO format)
                },
                ...
            ],
            "count": int,
            "status": str
        }

    Raises:
        ValueError: If parameters are invalid
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        logger.warning("list_tasks_invalid_user_id", user_id=user_id)
        return {
            "error": "invalid_user_id",
            "message": "User ID is required and must be a string",
        }

    # Validate status filter
    valid_statuses = ["all", "pending", "completed"]
    if status not in valid_statuses:
        logger.warning("list_tasks_invalid_status", user_id=user_id, status=status)
        return {
            "error": "invalid_status",
            "message": f"Status must be one of: {', '.join(valid_statuses)}",
        }

    db: Session = SessionLocal()
    try:
        # Fetch tasks from database (filtering done at SQL level)
        tasks = TaskRepository.list_by_user(db, user_id, status=status)

        # Format response
        task_list = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
            }
            for task in tasks
        ]

        logger.info(
            "list_tasks_success", user_id=user_id, status=status, count=len(task_list)
        )

        return {"tasks": task_list, "count": len(task_list), "status": status}

    except Exception as e:
        logger.error("list_tasks_failed", user_id=user_id, status=status, error=str(e))
        return {"error": "task_retrieval_failed", "message": "Failed to retrieve tasks"}

    finally:
        db.close()
