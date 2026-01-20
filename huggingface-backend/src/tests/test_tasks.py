"""
Task CRUD Endpoint Tests
Phase II - Todo Full-Stack Web Application

Tests for all task-related endpoints:
- POST /api/tasks (create)
- GET /api/tasks (list)
- GET /api/tasks/{id} (get single)
- PUT /api/tasks/{id} (update)
- DELETE /api/tasks/{id} (delete)
- PATCH /api/tasks/{id}/complete (toggle completion)
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from jose import jwt
import os

from main import app
from db import get_session
from models import User, Task
from middleware.auth import get_current_user_id


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_session():
    """
    Create a test database session for each test.
    Uses in-memory SQLite database.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
def client(test_session):
    """
    Create a test client for API requests.
    """
    def override_get_session():
        return test_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_token():
    """
    Generate a valid JWT token for a test user.
    """
    secret = os.getenv("BETTER_AUTH_SECRET", "test-secret")
    payload = {
        "sub": "test-user-123",
        "email": "test@example.com",
        "iat": 1234567890,
        "exp": 9999999999
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


@pytest.fixture
def test_user_2_token():
    """
    Generate a valid JWT token for a second test user.
    """
    secret = os.getenv("BETTER_AUTH_SECRET", "test-secret")
    payload = {
        "sub": "test-user-456",
        "email": "user2@example.com",
        "iat": 1234567890,
        "exp": 9999999999
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


@pytest.fixture
def auth_headers(test_user_token):
    """
    Generate authorization headers with Bearer token.
    """
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def auth_headers_user_2(test_user_2_token):
    """
    Generate authorization headers for second user.
    """
    return {"Authorization": f"Bearer {test_user_2_token}"}


# ============================================================================
# Create Task Tests (POST /api/tasks)
# ============================================================================

def test_create_task_success(client, auth_headers):
    """
    Test creating a task with valid data.
    Should return 201 with task object.
    """
    response = client.post(
        "/api/tasks",
        json={
            "title": "Test Task",
            "description": "This is a test task"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["completed"] is False
    assert "created_at" in data
    assert "updated_at" in data
    assert data["user_id"] == "test-user-123"


def test_create_task_without_description(client, auth_headers):
    """
    Test creating a task without optional description.
    Should return 201 with task object.
    """
    response = client.post(
        "/api/tasks",
        json={"title": "Task without description"},
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Task without description"
    assert data["description"] is None


def test_create_task_missing_title(client, auth_headers):
    """
    Test creating a task without required title.
    Should return 400 Bad Request.
    """
    response = client.post(
        "/api/tasks",
        json={"description": "No title"},
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "title" in response.json()["detail"].lower()


def test_create_task_empty_title(client, auth_headers):
    """
    Test creating a task with empty title.
    Should return 400 Bad Request.
    """
    response = client.post(
        "/api/tasks",
        json={"title": "   "},
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "title" in response.json()["detail"].lower()


def test_create_task_title_too_long(client, auth_headers):
    """
    Test creating a task with title exceeding 200 characters.
    Should return 400 Bad Request.
    """
    response = client.post(
        "/api/tasks",
        json={"title": "A" * 201},
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "title" in response.json()["detail"].lower()


def test_create_task_description_too_long(client, auth_headers):
    """
    Test creating a task with description exceeding 1000 characters.
    Should return 400 Bad Request.
    """
    response = client.post(
        "/api/tasks",
        json={
            "title": "Valid title",
            "description": "A" * 1001
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "description" in response.json()["detail"].lower()


def test_create_task_unauthorized(client):
    """
    Test creating a task without authentication.
    Should return 401 Unauthorized.
    """
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task"}
    )

    assert response.status_code == 401


def test_create_task_invalid_token(client):
    """
    Test creating a task with invalid JWT token.
    Should return 401 Unauthorized.
    """
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401


# ============================================================================
# List Tasks Tests (GET /api/tasks)
# ============================================================================

def test_list_tasks_empty(client, auth_headers):
    """
    Test listing tasks when user has no tasks.
    Should return 200 with empty array.
    """
    response = client.get("/api/tasks", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert data["tasks"] == []


def test_list_tasks_with_data(client, auth_headers):
    """
    Test listing tasks when user has multiple tasks.
    Should return 200 with all user's tasks.
    """
    # Create 3 tasks
    for i in range(3):
        client.post(
            "/api/tasks",
            json={"title": f"Task {i + 1}"},
            headers=auth_headers
        )

    response = client.get("/api/tasks", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 3


def test_list_tasks_user_isolation(client, auth_headers, auth_headers_user_2):
    """
    Test that users can only see their own tasks.
    User A creates tasks, User B should see empty list.
    """
    # User A creates 2 tasks
    client.post(
        "/api/tasks",
        json={"title": "User A Task 1"},
        headers=auth_headers
    )
    client.post(
        "/api/tasks",
        json={"title": "User A Task 2"},
        headers=auth_headers
    )

    # User B creates 1 task
    client.post(
        "/api/tasks",
        json={"title": "User B Task 1"},
        headers=auth_headers_user_2
    )

    # User A should see 2 tasks
    response_a = client.get("/api/tasks", headers=auth_headers)
    assert len(response_a.json()["tasks"]) == 2

    # User B should see 1 task
    response_b = client.get("/api/tasks", headers=auth_headers_user_2)
    assert len(response_b.json()["tasks"]) == 1


def test_list_tasks_sorted_by_created_at_desc(client, auth_headers):
    """
    Test that tasks are sorted by created_at in descending order (newest first).
    """
    # Create tasks with different titles
    client.post("/api/tasks", json={"title": "First Task"}, headers=auth_headers)
    client.post("/api/tasks", json={"title": "Second Task"}, headers=auth_headers)
    client.post("/api/tasks", json={"title": "Third Task"}, headers=auth_headers)

    response = client.get("/api/tasks", headers=auth_headers)
    tasks = response.json()["tasks"]

    # Newest task should be first
    assert tasks[0]["title"] == "Third Task"
    assert tasks[1]["title"] == "Second Task"
    assert tasks[2]["title"] == "First Task"


def test_list_tasks_unauthorized(client):
    """
    Test listing tasks without authentication.
    Should return 401 Unauthorized.
    """
    response = client.get("/api/tasks")
    assert response.status_code == 401


# ============================================================================
# Get Single Task Tests (GET /api/tasks/{id})
# ============================================================================

def test_get_task_success(client, auth_headers):
    """
    Test getting a single task by ID.
    Should return 200 with task object.
    """
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"title": "Test Task"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # Get the task
    response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"


def test_get_task_not_found(client, auth_headers):
    """
    Test getting a task that doesn't exist.
    Should return 404 Not Found.
    """
    response = client.get("/api/tasks/99999", headers=auth_headers)
    assert response.status_code == 404


def test_get_task_permission_denied(client, auth_headers, auth_headers_user_2):
    """
    Test getting a task owned by another user.
    Should return 404 Not Found (user isolation).
    """
    # User A creates a task
    create_response = client.post(
        "/api/tasks",
        json={"title": "User A Task"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # User B tries to get User A's task
    response = client.get(f"/api/tasks/{task_id}", headers=auth_headers_user_2)
    assert response.status_code == 404


def test_get_task_unauthorized(client):
    """
    Test getting a task without authentication.
    Should return 401 Unauthorized.
    """
    response = client.get("/api/tasks/1")
    assert response.status_code == 401


# ============================================================================
# Update Task Tests (PUT /api/tasks/{id})
# ============================================================================

def test_update_task_success(client, auth_headers):
    """
    Test updating a task with valid data.
    Should return 200 with updated task.
    """
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"title": "Original Title", "description": "Original Description"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # Update the task
    response = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "Updated Title", "description": "Updated Description"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["updated_at"] != data["created_at"]


def test_update_task_title_only(client, auth_headers):
    """
    Test updating only the title.
    Should return 200 with updated title, description unchanged.
    """
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"title": "Original", "description": "Keep this"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # Update only title
    response = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "New Title"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "Keep this"


def test_update_task_description_only(client, auth_headers):
    """
    Test updating only the description.
    Should return 200 with updated description, title unchanged.
    """
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"title": "Keep this", "description": "Original"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # Update only description
    response = client.put(
        f"/api/tasks/{task_id}",
        json={"description": "New Description"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Keep this"
    assert data["description"] == "New Description"


def test_update_task_invalid_title(client, auth_headers):
    """
    Test updating a task with invalid title (too long).
    Should return 400 Bad Request.
    """
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"title": "Original"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # Update with invalid title
    response = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "A" * 201},
        headers=auth_headers
    )

    assert response.status_code == 400


def test_update_task_not_found(client, auth_headers):
    """
    Test updating a task that doesn't exist.
    Should return 404 Not Found.
    """
    response = client.put(
        "/api/tasks/99999",
        json={"title": "Updated"},
        headers=auth_headers
    )
    assert response.status_code == 404


def test_update_task_permission_denied(client, auth_headers, auth_headers_user_2):
    """
    Test updating a task owned by another user.
    Should return 403 Forbidden.
    """
    # User A creates a task
    create_response = client.post(
        "/api/tasks",
        json={"title": "User A Task"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # User B tries to update User A's task
    response = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "Hacked!"},
        headers=auth_headers_user_2
    )
    assert response.status_code == 403


def test_update_task_unauthorized(client):
    """
    Test updating a task without authentication.
    Should return 401 Unauthorized.
    """
    response = client.put(
        "/api/tasks/1",
        json={"title": "Updated"}
    )
    assert response.status_code == 401


# ============================================================================
# Delete Task Tests (DELETE /api/tasks/{id})
# ============================================================================

def test_delete_task_success(client, auth_headers):
    """
    Test deleting a task.
    Should return 204 No Content.
    """
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"title": "To be deleted"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # Delete the task
    response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify task is deleted
    get_response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_task_not_found(client, auth_headers):
    """
    Test deleting a task that doesn't exist.
    Should return 404 Not Found.
    """
    response = client.delete("/api/tasks/99999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_task_permission_denied(client, auth_headers, auth_headers_user_2):
    """
    Test deleting a task owned by another user.
    Should return 403 Forbidden.
    """
    # User A creates a task
    create_response = client.post(
        "/api/tasks",
        json={"title": "User A Task"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # User B tries to delete User A's task
    response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers_user_2)
    assert response.status_code == 403


def test_delete_task_unauthorized(client):
    """
    Test deleting a task without authentication.
    Should return 401 Unauthorized.
    """
    response = client.delete("/api/tasks/1")
    assert response.status_code == 401


# ============================================================================
# Toggle Complete Tests (PATCH /api/tasks/{id}/complete)
# ============================================================================

def test_toggle_complete_pending_to_completed(client, auth_headers):
    """
    Test toggling task from pending to completed.
    Should return 200 with completed=True.
    """
    # Create a task (initially pending)
    create_response = client.post(
        "/api/tasks",
        json={"title": "Test Task"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # Toggle to completed
    response = client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True
    assert data["updated_at"] != data["created_at"]


def test_toggle_complete_completed_to_pending(client, auth_headers):
    """
    Test toggling task from completed back to pending.
    Should return 200 with completed=False.
    """
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"title": "Test Task"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # Toggle to completed
    client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)

    # Toggle back to pending
    response = client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is False


def test_toggle_complete_not_found(client, auth_headers):
    """
    Test toggling completion for a task that doesn't exist.
    Should return 404 Not Found.
    """
    response = client.patch("/api/tasks/99999/complete", headers=auth_headers)
    assert response.status_code == 404


def test_toggle_complete_permission_denied(client, auth_headers, auth_headers_user_2):
    """
    Test toggling completion for a task owned by another user.
    Should return 403 Forbidden.
    """
    # User A creates a task
    create_response = client.post(
        "/api/tasks",
        json={"title": "User A Task"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # User B tries to toggle User A's task
    response = client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers_user_2)
    assert response.status_code == 403


def test_toggle_complete_unauthorized(client):
    """
    Test toggling completion without authentication.
    Should return 401 Unauthorized.
    """
    response = client.patch("/api/tasks/1/complete")
    assert response.status_code == 401


# ============================================================================
# Integration Tests (Full Workflows)
# ============================================================================

def test_full_task_lifecycle(client, auth_headers):
    """
    Test complete task lifecycle: create → list → update → complete → delete.
    """
    # 1. Create task
    create_response = client.post(
        "/api/tasks",
        json={"title": "Lifecycle Task", "description": "Testing full flow"},
        headers=auth_headers
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # 2. List tasks (should include new task)
    list_response = client.get("/api/tasks", headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()["tasks"]) == 1

    # 3. Get single task
    get_response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Lifecycle Task"

    # 4. Update task
    update_response = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "Updated Lifecycle Task"},
        headers=auth_headers
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Lifecycle Task"

    # 5. Toggle completion
    complete_response = client.patch(
        f"/api/tasks/{task_id}/complete",
        headers=auth_headers
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["completed"] is True

    # 6. Delete task
    delete_response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    # 7. Verify deletion
    verify_response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert verify_response.status_code == 404


def test_multiple_users_isolation(client, auth_headers, auth_headers_user_2):
    """
    Test complete user isolation across all operations.
    """
    # User A creates 2 tasks
    task_a1 = client.post(
        "/api/tasks",
        json={"title": "User A Task 1"},
        headers=auth_headers
    ).json()["id"]

    task_a2 = client.post(
        "/api/tasks",
        json={"title": "User A Task 2"},
        headers=auth_headers
    ).json()["id"]

    # User B creates 1 task
    task_b1 = client.post(
        "/api/tasks",
        json={"title": "User B Task 1"},
        headers=auth_headers_user_2
    ).json()["id"]

    # User A lists tasks (should see only 2)
    user_a_tasks = client.get("/api/tasks", headers=auth_headers).json()["tasks"]
    assert len(user_a_tasks) == 2

    # User B lists tasks (should see only 1)
    user_b_tasks = client.get("/api/tasks", headers=auth_headers_user_2).json()["tasks"]
    assert len(user_b_tasks) == 1

    # User B cannot access User A's tasks
    assert client.get(f"/api/tasks/{task_a1}", headers=auth_headers_user_2).status_code == 404
    assert client.put(
        f"/api/tasks/{task_a1}",
        json={"title": "Hacked"},
        headers=auth_headers_user_2
    ).status_code == 403
    assert client.delete(f"/api/tasks/{task_a1}", headers=auth_headers_user_2).status_code == 403
    assert client.patch(f"/api/tasks/{task_a1}/complete", headers=auth_headers_user_2).status_code == 403

    # User A cannot access User B's tasks
    assert client.get(f"/api/tasks/{task_b1}", headers=auth_headers).status_code == 404
    assert client.put(
        f"/api/tasks/{task_b1}",
        json={"title": "Hacked"},
        headers=auth_headers
    ).status_code == 403
