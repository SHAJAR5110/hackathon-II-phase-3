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
    task_id: int = None,
    task_name: str = None,
) -> dict:
    """
    Delete a task by ID or by name

    Parameters:
        user_id (str, required): The user ID
        task_id (int, optional): The task ID to delete
        task_name (str, optional): The task name/title to delete

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

    # Must provide either task_id or task_name
    if not task_id and not task_name:
        logger.warning("delete_task_missing_params", user_id=user_id)
        return {
            "error": "missing_params",
            "message": "Either task_id or task_name must be provided",
        }

    if task_id and (not isinstance(task_id, int) or task_id <= 0):
        logger.warning("delete_task_invalid_task_id", user_id=user_id, task_id=task_id)
        return {
            "error": "invalid_task_id",
            "message": "Task ID must be a positive integer",
        }

    if task_name and not isinstance(task_name, str):
        logger.warning("delete_task_invalid_task_name", user_id=user_id, task_name=task_name)
        return {
            "error": "invalid_task_name",
            "message": "Task name must be a string",
        }

    db: Session = SessionLocal()
    try:
        task = None

        # If task_id provided, fetch by ID
        if task_id:
            task = TaskRepository.read(db, user_id, task_id)
            if not task:
                logger.warning("delete_task_not_found", user_id=user_id, task_id=task_id)
                return {"error": "task_not_found", "message": f"Task {task_id} not found"}

        # If task_name provided, search by name
        elif task_name:
            # Get all tasks and find matching one
            from sqlalchemy import select, func
            from ...models import Task

            # Try exact match first
            statement = select(Task).where(
                (Task.user_id == user_id) &
                (Task.title == task_name)
            )
            task = db.exec(statement).first()

            # If no exact match, try case-insensitive match
            if not task:
                statement = select(Task).where(
                    (Task.user_id == user_id) &
                    (func.lower(Task.title) == func.lower(task_name))
                )
                task = db.exec(statement).first()

            if not task:
                logger.warning(
                    "delete_task_not_found_by_name",
                    user_id=user_id,
                    task_name=task_name
                )
                return {
                    "error": "task_not_found",
                    "message": f"Task with name '{task_name}' not found"
                }
            task_id = task.id

        # Store task info before deletion
        task_title = task.title
        task_id_val = task.id

        # Delete task using raw database operation to ensure proper transaction
        try:
            # Use SQLAlchemy delete directly for better control
            from sqlalchemy import delete as sql_delete
            from ...models import Task as TaskModel

            # Execute delete statement
            delete_stmt = sql_delete(TaskModel).where(
                (TaskModel.id == task_id) & (TaskModel.user_id == user_id)
            )
            result = db.execute(delete_stmt)

            # Flush and commit to ensure immediate persistence
            db.flush()
            db.commit()

            # Verify deletion by checking if rows were affected
            if result.rowcount == 0:
                logger.warning(
                    "delete_task_failed_to_delete", user_id=user_id, task_id=task_id
                )
                return {
                    "error": "task_deletion_failed",
                    "message": f"Failed to delete task",
                }

            logger.info(
                "delete_task_success",
                user_id=user_id,
                task_id=task_id,
                title=task_title,
                by="id" if task_id else "name",
                rows_affected=result.rowcount
            )

            return {"task_id": task_id_val, "status": "deleted", "title": task_title}

        except Exception as delete_error:
            db.rollback()
            logger.error(
                "delete_task_sql_failed",
                user_id=user_id,
                task_id=task_id,
                error=str(delete_error)
            )
            return {
                "error": "task_deletion_failed",
                "message": f"Failed to delete task"
            }

    except Exception as e:
        logger.error(
            "delete_task_failed",
            user_id=user_id,
            task_id=task_id,
            task_name=task_name,
            error=str(e)
        )
        return {"error": "task_deletion_failed", "message": "Failed to delete task"}

    finally:
        db.close()
