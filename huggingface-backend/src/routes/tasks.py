"""
Task CRUD API Routes
Phase II - Todo Full-Stack Web Application

Implements all task management endpoints with user isolation and JWT authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
from typing import Optional

from ..db import get_session
from ..middleware.auth import get_current_user_id
from ..models import (
    Task,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse
)

router = APIRouter(prefix="/api", tags=["Tasks"])


# ============================================================================
# GET /api/tasks - List all tasks for authenticated user
# ============================================================================

@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: all, pending, completed"),
    sort_by: Optional[str] = Query("created", alias="sort", description="Sort by: created, title, updated"),
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Retrieve all tasks belonging to the authenticated user.

    Query Parameters:
        - status: Filter by completion status (all, pending, completed). Default: all
        - sort: Sort order (created, title, updated). Default: created (newest first)

    Returns:
        TaskListResponse: Object containing array of tasks

    Security:
        - Requires valid JWT token
        - Returns only tasks owned by authenticated user (user isolation)

    Example:
        GET /api/tasks?status=pending&sort=title
        Authorization: Bearer <token>
    """
    # Build base query filtered by user_id (USER ISOLATION)
    statement = select(Task).where(Task.user_id == user_id)

    # Apply status filter
    if status_filter == "pending":
        statement = statement.where(Task.completed == False)
    elif status_filter == "completed":
        statement = statement.where(Task.completed == True)
    # "all" or None: no additional filter

    # Apply sorting
    if sort_by == "title":
        statement = statement.order_by(Task.title.asc())
    elif sort_by == "updated":
        statement = statement.order_by(Task.updated_at.desc())
    else:  # Default: created (newest first)
        statement = statement.order_by(Task.created_at.desc())

    # Execute query
    result = await session.execute(statement)
    tasks = result.scalars().all()

    return TaskListResponse(tasks=tasks)


# ============================================================================
# POST /api/tasks - Create a new task
# ============================================================================

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new task for the authenticated user.

    Request Body:
        - title: Task title (required, 1-200 characters)
        - description: Task description (optional, max 1000 characters)

    Returns:
        TaskResponse: Created task with all fields

    Security:
        - Requires valid JWT token
        - Task is automatically associated with authenticated user

    Validation:
        - Title cannot be empty or whitespace only
        - Title and description are automatically trimmed

    Example:
        POST /api/tasks
        Authorization: Bearer <token>
        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread"
        }
    """
    # Create new task (automatically associated with user)
    new_task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return new_task


# ============================================================================
# GET /api/tasks/{task_id} - Get single task details
# ============================================================================

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Retrieve a single task by ID.

    Path Parameters:
        - task_id: ID of the task to retrieve

    Returns:
        TaskResponse: Task details

    Security:
        - Requires valid JWT token
        - Returns 404 if task doesn't exist OR belongs to another user (prevents info leakage)

    Example:
        GET /api/tasks/1
        Authorization: Bearer <token>
    """
    # Fetch task by ID
    task = await session.get(Task, task_id)

    # Check if task exists and belongs to authenticated user (USER ISOLATION)
    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


# ============================================================================
# PUT /api/tasks/{task_id} - Update a task
# ============================================================================

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update an existing task.

    Path Parameters:
        - task_id: ID of the task to update

    Request Body:
        - title: New task title (optional, 1-200 characters if provided)
        - description: New task description (optional, max 1000 characters if provided)

    Returns:
        TaskResponse: Updated task with all fields

    Security:
        - Requires valid JWT token
        - Returns 404 if task doesn't exist
        - Returns 403 if task belongs to another user (permission denied)

    Validation:
        - At least one field must be provided
        - Title cannot be empty if provided
        - Values are automatically trimmed

    Example:
        PUT /api/tasks/1
        Authorization: Bearer <token>
        {
            "title": "Buy groceries and cook dinner",
            "description": "Updated description"
        }
    """
    # Fetch task by ID
    task = await session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership (PERMISSION CHECK)
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this task"
        )

    # Validate that at least one field is provided
    if task_data.title is None and task_data.description is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (title or description) must be provided for update"
        )

    # Update fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


# ============================================================================
# DELETE /api/tasks/{task_id} - Delete a task
# ============================================================================

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a task permanently.

    Path Parameters:
        - task_id: ID of the task to delete

    Returns:
        None (204 No Content)

    Security:
        - Requires valid JWT token
        - Returns 404 if task doesn't exist
        - Returns 403 if task belongs to another user (permission denied)

    Note:
        - Deletion is permanent; no archive or soft delete in MVP
        - Returns 204 with no response body on success

    Example:
        DELETE /api/tasks/1
        Authorization: Bearer <token>
    """
    # Fetch task by ID
    task = await session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership (PERMISSION CHECK)
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this task"
        )

    # Delete task
    await session.delete(task)
    await session.commit()

    return None  # 204 No Content has no response body


# ============================================================================
# PATCH /api/tasks/{task_id}/complete - Toggle completion status
# ============================================================================

@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_complete(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Toggle task completion status.

    Path Parameters:
        - task_id: ID of the task to toggle

    Returns:
        TaskResponse: Updated task with new completion status

    Security:
        - Requires valid JWT token
        - Returns 404 if task doesn't exist
        - Returns 403 if task belongs to another user (permission denied)

    Behavior:
        - If task.completed = False, sets it to True
        - If task.completed = True, sets it to False
        - Updates updated_at timestamp

    Example:
        PATCH /api/tasks/1/complete
        Authorization: Bearer <token>
    """
    # Fetch task by ID
    task = await session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership (PERMISSION CHECK)
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this task"
        )

    # Toggle completion status
    task.completed = not task.completed

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task
