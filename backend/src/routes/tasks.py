"""
Task Management Endpoints for Todo Chatbot

Provides:
- GET /api/tasks - List all tasks for authenticated user
- GET /api/tasks/{task_id} - Get specific task
- POST /api/tasks - Create new task
- PATCH /api/tasks/{task_id} - Update task
- DELETE /api/tasks/{task_id} - Delete task
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel

from ..db import get_db_session as get_db
from ..logging_config import get_logger
from ..models import Task, User
from ..middleware.auth import get_current_user

logger = get_logger(__name__)

# Router
router = APIRouter(prefix="/api/tasks", tags=["tasks"])


# ============================================================================
# Request/Response Models
# ============================================================================


class TaskCreate(BaseModel):
    """Create task request"""

    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    """Update task request"""

    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """Task response"""

    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: str
    updated_at: str


# ============================================================================
# Endpoints
# ============================================================================


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    user_id: str = Depends(get_current_user),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List tasks for authenticated user

    Query parameters:
    - status: Filter by status ("all", "pending", "completed")
    """
    logger.info("list_tasks_requested", user_id=user_id, status=status)

    # Build query
    statement = select(Task).where(Task.user_id == user_id)

    # Apply status filter
    if status == "completed":
        statement = statement.where(Task.completed == True)
    elif status == "pending":
        statement = statement.where(Task.completed == False)
    # "all" or None: no filter

    # Order by creation date (newest first)
    statement = statement.order_by(Task.created_at.desc())

    tasks = db.exec(statement).all()

    logger.info("tasks_listed", user_id=user_id, task_count=len(tasks))

    return [
        TaskResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
        )
        for task in tasks
    ]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get specific task by ID"""
    logger.info("get_task_requested", user_id=user_id, task_id=task_id)

    statement = select(Task).where(
        (Task.id == task_id) & (Task.user_id == user_id)
    )
    task = db.exec(statement).first()

    if not task:
        logger.warning(
            "task_not_found", user_id=user_id, task_id=task_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new task"""
    logger.info(
        "create_task_requested",
        user_id=user_id,
        title=request.title,
    )

    # Verify user exists
    statement = select(User).where(User.user_id == user_id)
    user = db.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Create task
    task = Task(
        user_id=user_id,
        title=request.title,
        description=request.description or "",
        completed=False,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    logger.info(
        "task_created",
        user_id=user_id,
        task_id=task.id,
        title=task.title,
    )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    request: TaskUpdate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update task"""
    logger.info(
        "update_task_requested",
        user_id=user_id,
        task_id=task_id,
    )

    # Find task
    statement = select(Task).where(
        (Task.id == task_id) & (Task.user_id == user_id)
    )
    task = db.exec(statement).first()

    if not task:
        logger.warning(
            "task_not_found_for_update",
            user_id=user_id,
            task_id=task_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update fields
    if request.title is not None:
        task.title = request.title
    if request.description is not None:
        task.description = request.description
    if request.completed is not None:
        task.completed = request.completed

    db.add(task)
    db.commit()
    db.refresh(task)

    logger.info(
        "task_updated",
        user_id=user_id,
        task_id=task.id,
        title=task.title,
    )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete task"""
    logger.info(
        "delete_task_requested",
        user_id=user_id,
        task_id=task_id,
    )

    # Find task
    statement = select(Task).where(
        (Task.id == task_id) & (Task.user_id == user_id)
    )
    task = db.exec(statement).first()

    if not task:
        logger.warning(
            "task_not_found_for_delete",
            user_id=user_id,
            task_id=task_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()

    logger.info(
        "task_deleted",
        user_id=user_id,
        task_id=task_id,
        title=task.title,
    )
