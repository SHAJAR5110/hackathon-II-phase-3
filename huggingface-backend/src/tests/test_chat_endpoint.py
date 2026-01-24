"""
Integration Tests for Chat Endpoint & User Stories
Tests all 6 user story flows end-to-end with database
Feature: 1-chatbot-ai
"""

import json
from datetime import datetime
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..main import app
from ..models import Conversation, Message, Task, User
from ..repositories import (
    ConversationRepository,
    MessageRepository,
    TaskRepository,
)

# Test client
client = TestClient(app)

# Test user ID and headers
TEST_USER_ID = "testuser123"
TEST_AUTH_HEADER = {"Authorization": f"Bearer {TEST_USER_ID}"}


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def db_session():
    """Provide clean database session for tests"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def test_user(db_session: Session):
    """Create test user"""
    user = User(user_id=TEST_USER_ID)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_conversation(db_session: Session, test_user: User):
    """Create test conversation"""
    conversation = Conversation(user_id=test_user.user_id)
    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)
    return conversation


@pytest.fixture
def test_tasks(db_session: Session, test_user: User):
    """Create test tasks"""
    task1 = Task(
        user_id=test_user.user_id,
        title="Buy groceries",
        description="milk, eggs, bread",
        completed=False,
    )
    task2 = Task(
        user_id=test_user.user_id,
        title="Call mom",
        description=None,
        completed=False,
    )
    task3 = Task(
        user_id=test_user.user_id,
        title="Finish project",
        description="deadline: Friday",
        completed=True,
    )
    db_session.add_all([task1, task2, task3])
    db_session.commit()
    for task in [task1, task2, task3]:
        db_session.refresh(task)
    return [task1, task2, task3]


# ============================================================================
# Test: Endpoint Foundation (T029-T034)
# ============================================================================


class TestEndpointFoundation:
    """Tests for chat endpoint skeleton and foundation"""

    def test_chat_endpoint_requires_auth(self, db_session: Session, test_user: User):
        """T029: Chat endpoint requires authentication"""
        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Hello"},
        )
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_chat_endpoint_user_mismatch(self, db_session: Session, test_user: User):
        """T029: Chat endpoint rejects mismatched user_id"""
        response = client.post(
            f"/api/otheruser/chat",
            json={"message": "Hello"},
            headers=TEST_AUTH_HEADER,
        )
        assert response.status_code == 401

    def test_chat_endpoint_invalid_message(self, db_session: Session, test_user: User):
        """T029: Chat endpoint rejects invalid message"""
        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": ""},
            headers=TEST_AUTH_HEADER,
        )
        assert response.status_code == 422

    @patch("backend.src.routes.chat.AgentRunner")
    def test_chat_endpoint_creates_response(
        self, mock_runner_class, db_session: Session, test_user: User
    ):
        """T029-T034: Chat endpoint returns valid response"""
        # Mock agent runner
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)

        # Mock agent response
        mock_response = MagicMock()
        mock_response.response = "I've added task"
        mock_response.tool_calls = [{"tool": "add_task", "params": {"title": "Test"}}]
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Add a task"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "response" in data
        assert "tool_calls" in data
        assert data["conversation_id"] > 0

    @patch("backend.src.routes.chat.AgentRunner")
    def test_chat_endpoint_creates_conversation(
        self, mock_runner_class, db_session: Session, test_user: User
    ):
        """T030: Chat endpoint creates new conversation when not provided"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = "Hello"
        mock_response.tool_calls = []
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Hello"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        conversation_id = response.json()["conversation_id"]

        # Verify conversation was created
        conversation = ConversationRepository.read(
            db_session, TEST_USER_ID, conversation_id
        )
        assert conversation is not None
        assert conversation.user_id == TEST_USER_ID

    @patch("backend.src.routes.chat.AgentRunner")
    def test_chat_endpoint_loads_conversation(
        self,
        mock_runner_class,
        db_session: Session,
        test_user: User,
        test_conversation: Conversation,
    ):
        """T030: Chat endpoint loads existing conversation"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = "Hello again"
        mock_response.tool_calls = []
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Hello", "conversation_id": test_conversation.id},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        assert response.json()["conversation_id"] == test_conversation.id

    @patch("backend.src.routes.chat.AgentRunner")
    def test_chat_endpoint_stores_messages(
        self, mock_runner_class, db_session: Session, test_user: User
    ):
        """T031-T033: Chat endpoint stores user and assistant messages"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = "Assistant says hello"
        mock_response.tool_calls = []
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "User says hello"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        conversation_id = response.json()["conversation_id"]

        # Verify messages were stored
        messages = MessageRepository.list_by_conversation(db_session, conversation_id)
        assert len(messages) == 2

        # Check user message
        user_message = next(m for m in messages if m.role == "user")
        assert user_message.content == "User says hello"
        assert user_message.user_id == TEST_USER_ID

        # Check assistant message
        assistant_message = next(m for m in messages if m.role == "assistant")
        assert assistant_message.content == "Assistant says hello"
        assert assistant_message.user_id == TEST_USER_ID

    @patch("backend.src.routes.chat.AgentRunner")
    def test_chat_endpoint_response_format(
        self, mock_runner_class, db_session: Session, test_user: User
    ):
        """T034: Chat endpoint formats response correctly"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = "Task added"
        mock_response.tool_calls = [
            {
                "tool": "add_task",
                "params": {"user_id": TEST_USER_ID, "title": "Buy milk"},
            }
        ]
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Add task to buy milk"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response format
        assert isinstance(data["conversation_id"], int)
        assert isinstance(data["response"], str)
        assert isinstance(data["tool_calls"], list)
        assert len(data["tool_calls"]) == 1
        assert data["tool_calls"][0]["tool"] == "add_task"
        assert isinstance(data["tool_calls"][0]["params"], dict)


# ============================================================================
# Test: User Story 1 - Add Task (T035-T037)
# ============================================================================


class TestUserStory1AddTask:
    """Tests for add_task user story"""

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us1_basic_add_task(
        self, mock_runner_class, db_session: Session, test_user: User
    ):
        """T035: Basic add_task flow"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = "I've added 'Buy groceries' to your task list!"
        mock_response.tool_calls = [
            {
                "tool": "add_task",
                "params": {
                    "user_id": TEST_USER_ID,
                    "title": "Buy groceries",
                    "description": None,
                },
            }
        ]
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Add a task to buy groceries"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "added" in data["response"].lower()
        assert len(data["tool_calls"]) > 0
        assert data["tool_calls"][0]["tool"] == "add_task"

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us1_add_task_with_description(
        self, mock_runner_class, db_session: Session, test_user: User
    ):
        """T036: Add task with description"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = "I've added 'Buy groceries with milk, eggs, and bread'"
        mock_response.tool_calls = [
            {
                "tool": "add_task",
                "params": {
                    "user_id": TEST_USER_ID,
                    "title": "Buy groceries",
                    "description": "milk, eggs, and bread",
                },
            }
        ]
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Add a task to buy groceries with milk, eggs, and bread"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        tool_call = data["tool_calls"][0]
        assert tool_call["params"]["description"] == "milk, eggs, and bread"

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us1_ambiguous_add_request(
        self, mock_runner_class, db_session: Session, test_user: User
    ):
        """T037: Handle ambiguous add request"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = "What would you like to add?"
        mock_response.tool_calls = []  # No tool call yet
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Add something"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "add" in data["response"].lower()
        assert len(data["tool_calls"]) == 0  # No tool called


# ============================================================================
# Test: User Story 2 - List Tasks (T038-T040)
# ============================================================================


class TestUserStory2ListTasks:
    """Tests for list_tasks user story"""

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us2_list_all_tasks(
        self,
        mock_runner_class,
        db_session: Session,
        test_user: User,
        test_tasks,
    ):
        """T038: List all tasks"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = (
            "You have 3 tasks: 1) Buy groceries, 2) Call mom, 3) Finish project"
        )
        mock_response.tool_calls = [
            {"tool": "list_tasks", "params": {"user_id": TEST_USER_ID, "status": "all"}}
        ]
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Show me all my tasks"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "Buy groceries" in data["response"]
        assert "Call mom" in data["response"]
        assert "Finish project" in data["response"]

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us2_list_pending_tasks(
        self,
        mock_runner_class,
        db_session: Session,
        test_user: User,
        test_tasks,
    ):
        """T039: List pending tasks"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = (
            "You have 2 pending tasks: 1) Buy groceries, 2) Call mom"
        )
        mock_response.tool_calls = [
            {
                "tool": "list_tasks",
                "params": {"user_id": TEST_USER_ID, "status": "pending"},
            }
        ]
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "What's pending?"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "pending" in data["response"].lower()
        assert "Buy groceries" in data["response"]
        assert "Call mom" in data["response"]
        assert "Finish project" not in data["response"]

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us2_empty_task_list(
        self, mock_runner_class, db_session: Session, test_user: User
    ):
        """T040: Handle empty task list"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = "You have no tasks yet. Want to add one?"
        mock_response.tool_calls = [
            {"tool": "list_tasks", "params": {"user_id": TEST_USER_ID, "status": "all"}}
        ]
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Show me all my tasks"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "no tasks" in data["response"].lower()


# ============================================================================
# Test: User Story 3 - Complete Task (T041-T043)
# ============================================================================


class TestUserStory3CompleteTask:
    """Tests for complete_task user story"""

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us3_complete_by_id(
        self,
        mock_runner_class,
        db_session: Session,
        test_user: User,
        test_tasks,
    ):
        """T041: Complete task by ID"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = "I've marked 'Buy groceries' as complete!"
        mock_response.tool_calls = [
            {
                "tool": "complete_task",
                "params": {"user_id": TEST_USER_ID, "task_id": test_tasks[0].id},
            }
        ]
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": f"Mark task {test_tasks[0].id} as complete"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "marked" in data["response"].lower()
        assert "complete" in data["response"].lower()

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us3_complete_ambiguous_reference(
        self,
        mock_runner_class,
        db_session: Session,
        test_user: User,
        test_tasks,
    ):
        """T042: Handle ambiguous task reference"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = (
            "I found 'Call mom' task. Is that the one you finished?"
        )
        mock_response.tool_calls = [
            {"tool": "list_tasks", "params": {"user_id": TEST_USER_ID}}
        ]
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "I finished the mom task"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "mom" in data["response"].lower()

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us3_task_not_found(
        self, mock_runner_class, db_session: Session, test_user: User
    ):
        """T043: Handle task not found"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = (
            "I couldn't find task 999. Here are your pending tasks: ..."
        )
        mock_response.tool_calls = []
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Mark task 999 as complete"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "couldn't find" in data["response"].lower()


# ============================================================================
# Test: User Story 4 - Update Task (T044-T045)
# ============================================================================


class TestUserStory4UpdateTask:
    """Tests for update_task user story"""

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us4_update_title(
        self,
        mock_runner_class,
        db_session: Session,
        test_user: User,
        test_tasks,
    ):
        """T044: Update task title"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = "I've updated task 1 to 'Call mom tonight'"
        mock_response.tool_calls = [
            {
                "tool": "update_task",
                "params": {
                    "user_id": TEST_USER_ID,
                    "task_id": test_tasks[0].id,
                    "title": "Call mom tonight",
                },
            }
        ]
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Change task 1 to 'Call mom tonight'"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "updated" in data["response"].lower()

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us4_update_description(
        self,
        mock_runner_class,
        db_session: Session,
        test_user: User,
        test_tasks,
    ):
        """T045: Update task description"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = "I've updated task 1 with the new details"
        mock_response.tool_calls = [
            {
                "tool": "update_task",
                "params": {
                    "user_id": TEST_USER_ID,
                    "task_id": test_tasks[0].id,
                    "description": "remember to buy organic milk",
                },
            }
        ]
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Add details to task 1: remember to buy organic milk"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "updated" in data["response"].lower()


# ============================================================================
# Test: User Story 5 - Delete Task (T046-T047)
# ============================================================================


class TestUserStory5DeleteTask:
    """Tests for delete_task user story"""

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us5_delete_by_id(
        self,
        mock_runner_class,
        db_session: Session,
        test_user: User,
        test_tasks,
    ):
        """T046: Delete task by ID"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = "I've deleted 'Buy groceries' task"
        mock_response.tool_calls = [
            {
                "tool": "delete_task",
                "params": {"user_id": TEST_USER_ID, "task_id": test_tasks[0].id},
            }
        ]
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": f"Delete task {test_tasks[0].id}"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["response"].lower()

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us5_delete_ambiguous(
        self,
        mock_runner_class,
        db_session: Session,
        test_user: User,
        test_tasks,
    ):
        """T047: Handle ambiguous delete"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = (
            "Which task would you like to delete? Here are your tasks: ..."
        )
        mock_response.tool_calls = [
            {"tool": "list_tasks", "params": {"user_id": TEST_USER_ID}}
        ]
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Delete the task"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "which" in data["response"].lower()


# ============================================================================
# Test: User Story 6 - Conversation Context (T048-T050)
# ============================================================================


class TestUserStory6ConversationContext:
    """Tests for conversation context user story"""

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us6_multi_turn_context(
        self,
        mock_runner_class,
        db_session: Session,
        test_user: User,
        test_conversation: Conversation,
    ):
        """T048: Multi-turn conversation with context"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)

        # Message 1: Add task
        mock_response1 = MagicMock()
        mock_response1.response = "I've added 'Buy groceries' to your task list!"
        mock_response1.tool_calls = [
            {
                "tool": "add_task",
                "params": {"user_id": TEST_USER_ID, "title": "Buy groceries"},
            }
        ]
        mock_response1.error = None

        # Message 2: List tasks
        mock_response2 = MagicMock()
        mock_response2.response = "You have 1 task: 1) Buy groceries"
        mock_response2.tool_calls = [
            {"tool": "list_tasks", "params": {"user_id": TEST_USER_ID, "status": "all"}}
        ]
        mock_response2.error = None

        # Message 3: Complete task
        mock_response3 = MagicMock()
        mock_response3.response = "I've marked 'Buy groceries' as complete!"
        mock_response3.tool_calls = [
            {"tool": "complete_task", "params": {"user_id": TEST_USER_ID, "task_id": 1}}
        ]
        mock_response3.error = None

        mock_runner.run = AsyncMock(
            side_effect=[mock_response1, mock_response2, mock_response3]
        )

        # Send three messages in same conversation
        response1 = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={
                "message": "Add a task to buy groceries",
                "conversation_id": test_conversation.id,
            },
            headers=TEST_AUTH_HEADER,
        )
        assert response1.status_code == 200

        response2 = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={
                "message": "Show me all my tasks",
                "conversation_id": test_conversation.id,
            },
            headers=TEST_AUTH_HEADER,
        )
        assert response2.status_code == 200

        response3 = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={
                "message": "Mark task 1 as complete",
                "conversation_id": test_conversation.id,
            },
            headers=TEST_AUTH_HEADER,
        )
        assert response3.status_code == 200

        # Verify all messages in conversation
        messages = MessageRepository.list_by_conversation(
            db_session, test_conversation.id
        )
        assert len(messages) == 6  # 3 user + 3 assistant

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us6_conversation_resume_after_refresh(
        self,
        mock_runner_class,
        db_session: Session,
        test_user: User,
    ):
        """T049: Conversation resume after page refresh"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)

        # Add prior messages to conversation
        conversation = ConversationRepository.create(db_session, TEST_USER_ID)
        for i in range(5):
            MessageRepository.create(
                db_session, TEST_USER_ID, conversation.id, "user", f"Message {i + 1}"
            )
            MessageRepository.create(
                db_session,
                TEST_USER_ID,
                conversation.id,
                "assistant",
                f"Response {i + 1}",
            )

        mock_response = MagicMock()
        mock_response.response = "I remember we added 'Buy groceries' earlier..."
        mock_response.tool_calls = []
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        # Request same conversation after "page refresh"
        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={
                "message": "What have we talked about?",
                "conversation_id": conversation.id,
            },
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200

        # Verify all prior messages still exist
        messages = MessageRepository.list_by_conversation(db_session, conversation.id)
        assert len(messages) == 11  # 5 user + 5 assistant + new user message

    @patch("backend.src.routes.chat.AgentRunner")
    def test_us6_server_restart_resilience(
        self,
        mock_runner_class,
        db_session: Session,
        test_user: User,
    ):
        """T050: Server restart resilience"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)

        # Add conversation with 10 messages to database
        conversation = ConversationRepository.create(db_session, TEST_USER_ID)
        for i in range(10):
            MessageRepository.create(
                db_session, TEST_USER_ID, conversation.id, "user", f"User msg {i + 1}"
            )
            MessageRepository.create(
                db_session,
                TEST_USER_ID,
                conversation.id,
                "assistant",
                f"Assistant msg {i + 1}",
            )

        # Simulate server restart by closing and reopening connection
        conversation_id = conversation.id
        db_session.close()

        # New "request" after server restart
        mock_response = MagicMock()
        mock_response.response = "I can see all our prior conversation history"
        mock_response.tool_calls = []
        mock_response.error = None
        mock_runner.run = AsyncMock(return_value=mock_response)

        # Create new session (simulating server restart)
        new_db = SessionLocal()
        try:
            response = client.post(
                f"/api/{TEST_USER_ID}/chat",
                json={
                    "message": "Can you see our history?",
                    "conversation_id": conversation_id,
                },
                headers=TEST_AUTH_HEADER,
            )

            assert response.status_code == 200
            data = response.json()

            # Verify all prior messages loaded
            messages = MessageRepository.list_by_conversation(new_db, conversation_id)
            assert len(messages) == 21  # 10 user + 10 assistant + new user message

        finally:
            new_db.close()


# ============================================================================
# Test: Error Handling
# ============================================================================


class TestErrorHandling:
    """Tests for error handling"""

    @patch("backend.src.routes.chat.AgentRunner")
    def test_agent_timeout_error(
        self, mock_runner_class, db_session: Session, test_user: User
    ):
        """Test agent execution timeout"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=True)
        mock_response = MagicMock()
        mock_response.response = "I'm taking too long to think. Please try again."
        mock_response.tool_calls = []
        mock_response.error = "timeout"
        mock_runner.run = AsyncMock(return_value=mock_response)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Hello"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 500

    @patch("backend.src.routes.chat.AgentRunner")
    def test_agent_initialization_failure(
        self, mock_runner_class, db_session: Session, test_user: User
    ):
        """Test agent initialization failure"""
        mock_runner = AsyncMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.initialize_agent = AsyncMock(return_value=False)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Hello"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 500
        data = response.json()
        assert "error" in data or "detail" in data

    def test_conversation_not_found(self, db_session: Session, test_user: User):
        """Test requesting non-existent conversation"""
        with patch("backend.src.routes.chat.AgentRunner") as mock_runner_class:
            mock_runner = AsyncMock()
            mock_runner_class.return_value = mock_runner
            mock_runner.initialize_agent = AsyncMock(return_value=True)

            response = client.post(
                f"/api/{TEST_USER_ID}/chat",
                json={"message": "Hello", "conversation_id": 99999},
                headers=TEST_AUTH_HEADER,
            )

            assert response.status_code == 500


# ============================================================================
# Test: User Isolation
# ============================================================================


class TestUserIsolation:
    """Tests for user isolation and security"""

    def test_user_cannot_access_other_user_conversation(self, db_session: Session):
        """Verify user A cannot access user B's conversation"""
        # Create user A and conversation
        user_a = User(user_id="usera")
        db_session.add(user_a)
        db_session.commit()

        conversation_a = Conversation(user_id="usera")
        db_session.add(conversation_a)
        db_session.commit()

        # User B attempts to access user A's conversation
        auth_header_b = {"Authorization": "Bearer userb"}

        with patch("backend.src.routes.chat.AgentRunner"):
            response = client.post(
                f"/api/userb/chat",
                json={"message": "Hello", "conversation_id": conversation_a.id},
                headers=auth_header_b,
            )

            assert response.status_code == 500  # Conversation not found


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
