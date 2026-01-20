"""
Unit tests for MCP Tools
Tests all task management tools with mock database
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from ..mcp_server.tools import (
    add_task,
    complete_task,
    delete_task,
    list_tasks,
    update_task,
)
from ..models import Task


class TestAddTaskTool:
    """Tests for add_task tool"""

    def test_add_task_success(self):
        """Test successful task creation"""
        with patch("src.mcp_server.tools.add_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.add_task.SessionLocal"):
                # Mock task creation
                mock_task = Mock()
                mock_task.id = 1
                mock_task.title = "Buy groceries"
                mock_repo.create.return_value = mock_task

                # Call tool
                result = add_task(
                    user_id="user123",
                    title="Buy groceries",
                    description="milk, eggs, bread",
                )

                # Verify result
                assert result["status"] == "created"
                assert result["task_id"] == 1
                assert result["title"] == "Buy groceries"
                assert "error" not in result

    def test_add_task_invalid_user_id(self):
        """Test add_task with invalid user_id"""
        result = add_task(user_id="", title="Test task")
        assert result["error"] == "invalid_user_id"

    def test_add_task_invalid_title(self):
        """Test add_task with invalid title"""
        result = add_task(user_id="user123", title="")
        assert result["error"] == "invalid_title"

    def test_add_task_title_too_long(self):
        """Test add_task with title exceeding 1000 chars"""
        long_title = "a" * 1001
        result = add_task(user_id="user123", title=long_title)
        assert result["error"] == "title_too_long"

    def test_add_task_description_too_long(self):
        """Test add_task with description exceeding 1000 chars"""
        long_description = "a" * 1001
        result = add_task(
            user_id="user123", title="Valid title", description=long_description
        )
        assert result["error"] == "description_too_long"

    def test_add_task_database_error(self):
        """Test add_task with database error"""
        with patch("src.mcp_server.tools.add_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.add_task.SessionLocal"):
                # Mock database error
                mock_repo.create.side_effect = Exception("DB Error")

                result = add_task(user_id="user123", title="Buy groceries")

                assert result["error"] == "task_creation_failed"


class TestListTasksTool:
    """Tests for list_tasks tool"""

    def test_list_tasks_all_success(self):
        """Test listing all tasks"""
        with patch("src.mcp_server.tools.list_tasks.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.list_tasks.SessionLocal"):
                # Mock task list
                mock_task1 = Mock()
                mock_task1.id = 1
                mock_task1.title = "Task 1"
                mock_task1.description = "Desc 1"
                mock_task1.completed = False
                mock_task1.created_at = datetime.utcnow()

                mock_task2 = Mock()
                mock_task2.id = 2
                mock_task2.title = "Task 2"
                mock_task2.description = "Desc 2"
                mock_task2.completed = True
                mock_task2.created_at = datetime.utcnow()

                mock_repo.list_by_user.return_value = [mock_task1, mock_task2]

                # Call tool
                result = list_tasks(user_id="user123", status="all")

                # Verify result
                assert result["count"] == 2
                assert len(result["tasks"]) == 2
                assert result["status"] == "all"
                assert result["tasks"][0]["title"] == "Task 1"
                assert result["tasks"][1]["title"] == "Task 2"
                assert "error" not in result

    def test_list_tasks_pending_filter(self):
        """Test listing pending tasks"""
        with patch("src.mcp_server.tools.list_tasks.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.list_tasks.SessionLocal"):
                mock_task = Mock()
                mock_task.id = 1
                mock_task.title = "Pending task"
                mock_task.description = None
                mock_task.completed = False
                mock_task.created_at = datetime.utcnow()

                mock_repo.list_by_user.return_value = [mock_task]

                result = list_tasks(user_id="user123", status="pending")

                assert result["status"] == "pending"
                assert result["count"] == 1
                assert result["tasks"][0]["completed"] == False

    def test_list_tasks_completed_filter(self):
        """Test listing completed tasks"""
        with patch("src.mcp_server.tools.list_tasks.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.list_tasks.SessionLocal"):
                mock_task = Mock()
                mock_task.id = 1
                mock_task.title = "Completed task"
                mock_task.description = None
                mock_task.completed = True
                mock_task.created_at = datetime.utcnow()

                mock_repo.list_by_user.return_value = [mock_task]

                result = list_tasks(user_id="user123", status="completed")

                assert result["status"] == "completed"
                assert result["count"] == 1
                assert result["tasks"][0]["completed"] == True

    def test_list_tasks_empty(self):
        """Test listing tasks with empty result"""
        with patch("src.mcp_server.tools.list_tasks.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.list_tasks.SessionLocal"):
                mock_repo.list_by_user.return_value = []

                result = list_tasks(user_id="user123", status="all")

                assert result["count"] == 0
                assert len(result["tasks"]) == 0

    def test_list_tasks_invalid_user_id(self):
        """Test list_tasks with invalid user_id"""
        result = list_tasks(user_id="", status="all")
        assert result["error"] == "invalid_user_id"

    def test_list_tasks_invalid_status(self):
        """Test list_tasks with invalid status"""
        result = list_tasks(user_id="user123", status="invalid")
        assert result["error"] == "invalid_status"


class TestCompleteTaskTool:
    """Tests for complete_task tool"""

    def test_complete_task_success(self):
        """Test successful task completion"""
        with patch("src.mcp_server.tools.complete_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.complete_task.SessionLocal"):
                # Mock read and update
                mock_task = Mock()
                mock_task.id = 1
                mock_task.title = "Buy groceries"

                mock_repo.read.return_value = mock_task
                mock_repo.update.return_value = mock_task

                result = complete_task(user_id="user123", task_id=1)

                assert result["status"] == "completed"
                assert result["task_id"] == 1
                assert result["title"] == "Buy groceries"
                assert "error" not in result

    def test_complete_task_not_found(self):
        """Test complete_task with non-existent task"""
        with patch("src.mcp_server.tools.complete_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.complete_task.SessionLocal"):
                mock_repo.read.return_value = None

                result = complete_task(user_id="user123", task_id=999)

                assert result["error"] == "task_not_found"

    def test_complete_task_invalid_user_id(self):
        """Test complete_task with invalid user_id"""
        result = complete_task(user_id="", task_id=1)
        assert result["error"] == "invalid_user_id"

    def test_complete_task_invalid_task_id(self):
        """Test complete_task with invalid task_id"""
        result = complete_task(user_id="user123", task_id=-1)
        assert result["error"] == "invalid_task_id"

    def test_complete_task_user_isolation(self):
        """Test that user cannot complete another user's task"""
        with patch("src.mcp_server.tools.complete_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.complete_task.SessionLocal"):
                # Simulate task belonging to different user
                mock_repo.read.return_value = None  # Task not found for user123

                result = complete_task(user_id="user123", task_id=1)

                assert result["error"] == "task_not_found"


class TestDeleteTaskTool:
    """Tests for delete_task tool"""

    def test_delete_task_success(self):
        """Test successful task deletion"""
        with patch("src.mcp_server.tools.delete_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.delete_task.SessionLocal"):
                # Mock read and delete
                mock_task = Mock()
                mock_task.id = 1
                mock_task.title = "Old task"

                mock_repo.read.return_value = mock_task
                mock_repo.delete.return_value = True

                result = delete_task(user_id="user123", task_id=1)

                assert result["status"] == "deleted"
                assert result["task_id"] == 1
                assert result["title"] == "Old task"
                assert "error" not in result

    def test_delete_task_not_found(self):
        """Test delete_task with non-existent task"""
        with patch("src.mcp_server.tools.delete_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.delete_task.SessionLocal"):
                mock_repo.read.return_value = None

                result = delete_task(user_id="user123", task_id=999)

                assert result["error"] == "task_not_found"

    def test_delete_task_invalid_user_id(self):
        """Test delete_task with invalid user_id"""
        result = delete_task(user_id="", task_id=1)
        assert result["error"] == "invalid_user_id"

    def test_delete_task_invalid_task_id(self):
        """Test delete_task with invalid task_id"""
        result = delete_task(user_id="user123", task_id=0)
        assert result["error"] == "invalid_task_id"

    def test_delete_task_user_isolation(self):
        """Test that user cannot delete another user's task"""
        with patch("src.mcp_server.tools.delete_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.delete_task.SessionLocal"):
                mock_repo.read.return_value = None

                result = delete_task(user_id="user123", task_id=1)

                assert result["error"] == "task_not_found"


class TestUpdateTaskTool:
    """Tests for update_task tool"""

    def test_update_task_title_success(self):
        """Test successful task title update"""
        with patch("src.mcp_server.tools.update_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.update_task.SessionLocal"):
                mock_task = Mock()
                mock_task.id = 1
                mock_task.title = "Updated title"

                mock_repo.read.return_value = mock_task
                mock_repo.update.return_value = mock_task

                result = update_task(
                    user_id="user123", task_id=1, title="Updated title"
                )

                assert result["status"] == "updated"
                assert result["task_id"] == 1
                assert result["title"] == "Updated title"
                assert "error" not in result

    def test_update_task_description_success(self):
        """Test successful task description update"""
        with patch("src.mcp_server.tools.update_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.update_task.SessionLocal"):
                mock_task = Mock()
                mock_task.id = 1
                mock_task.title = "Original title"

                mock_repo.read.return_value = mock_task
                mock_repo.update.return_value = mock_task

                result = update_task(
                    user_id="user123", task_id=1, description="Updated description"
                )

                assert result["status"] == "updated"
                assert "error" not in result

    def test_update_task_both_success(self):
        """Test successful update of both title and description"""
        with patch("src.mcp_server.tools.update_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.update_task.SessionLocal"):
                mock_task = Mock()
                mock_task.id = 1
                mock_task.title = "New title"

                mock_repo.read.return_value = mock_task
                mock_repo.update.return_value = mock_task

                result = update_task(
                    user_id="user123",
                    task_id=1,
                    title="New title",
                    description="New description",
                )

                assert result["status"] == "updated"
                assert "error" not in result

    def test_update_task_no_updates(self):
        """Test update_task with no parameters"""
        result = update_task(user_id="user123", task_id=1)
        assert result["error"] == "no_updates_provided"

    def test_update_task_not_found(self):
        """Test update_task with non-existent task"""
        with patch("src.mcp_server.tools.update_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.update_task.SessionLocal"):
                mock_repo.read.return_value = None

                result = update_task(user_id="user123", task_id=999, title="New title")

                assert result["error"] == "task_not_found"

    def test_update_task_title_too_long(self):
        """Test update_task with title exceeding 1000 chars"""
        long_title = "a" * 1001
        result = update_task(user_id="user123", task_id=1, title=long_title)
        assert result["error"] == "title_too_long"

    def test_update_task_description_too_long(self):
        """Test update_task with description exceeding 1000 chars"""
        long_description = "a" * 1001
        result = update_task(user_id="user123", task_id=1, description=long_description)
        assert result["error"] == "description_too_long"

    def test_update_task_invalid_user_id(self):
        """Test update_task with invalid user_id"""
        result = update_task(user_id="", task_id=1, title="New title")
        assert result["error"] == "invalid_user_id"

    def test_update_task_invalid_task_id(self):
        """Test update_task with invalid task_id"""
        result = update_task(user_id="user123", task_id=-1, title="New title")
        assert result["error"] == "invalid_task_id"

    def test_update_task_user_isolation(self):
        """Test that user cannot update another user's task"""
        with patch("src.mcp_server.tools.update_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.update_task.SessionLocal"):
                mock_repo.read.return_value = None

                result = update_task(user_id="user123", task_id=1, title="New title")

                assert result["error"] == "task_not_found"


class TestSchemaCompliance:
    """Tests for response schema compliance"""

    def test_add_task_response_schema(self):
        """Verify add_task response matches declared schema"""
        with patch("src.mcp_server.tools.add_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.add_task.SessionLocal"):
                mock_task = Mock()
                mock_task.id = 1
                mock_task.title = "Test"
                mock_repo.create.return_value = mock_task

                result = add_task(user_id="user123", title="Test")

                # Verify schema
                assert isinstance(result, dict)
                assert "task_id" in result
                assert "status" in result
                assert "title" in result
                assert isinstance(result["task_id"], int)
                assert isinstance(result["status"], str)
                assert isinstance(result["title"], str)

    def test_list_tasks_response_schema(self):
        """Verify list_tasks response matches declared schema"""
        with patch("src.mcp_server.tools.list_tasks.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.list_tasks.SessionLocal"):
                mock_repo.list_by_user.return_value = []

                result = list_tasks(user_id="user123", status="all")

                # Verify schema
                assert isinstance(result, dict)
                assert "tasks" in result
                assert "count" in result
                assert "status" in result
                assert isinstance(result["tasks"], list)
                assert isinstance(result["count"], int)

    def test_complete_task_response_schema(self):
        """Verify complete_task response matches declared schema"""
        with patch("src.mcp_server.tools.complete_task.TaskRepository") as mock_repo:
            with patch("src.mcp_server.tools.complete_task.SessionLocal"):
                mock_task = Mock()
                mock_task.id = 1
                mock_task.title = "Test"
                mock_repo.read.return_value = mock_task
                mock_repo.update.return_value = mock_task

                result = complete_task(user_id="user123", task_id=1)

                # Verify schema
                assert isinstance(result, dict)
                assert "task_id" in result
                assert "status" in result
                assert "title" in result
