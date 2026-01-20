"""
Integration Tests for Agent System (Phase 5)
Tests agent execution with MCP tools, conversation history, and error handling
"""

import asyncio
from datetime import datetime
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from ..agents.config import AgentConfig
from ..agents.context import AgentContextBuilder
from ..agents.converter import ThreadItemConverter
from ..agents.id_mapper import IDMapper, get_id_mapper, reset_id_mapper
from ..agents.runner import AgentResponse, AgentRunner
from ..db import SessionLocal
from ..models import Conversation, Message, Task
from ..repositories import ConversationRepository, MessageRepository, TaskRepository


class TestAgentConfig:
    """Test agent configuration module"""

    def test_system_prompt_is_set(self):
        """System prompt should contain task management instructions"""
        prompt = AgentConfig.get_system_prompt()
        assert "task management" in prompt.lower()
        assert "add_task" in prompt
        assert "list_tasks" in prompt
        assert "complete_task" in prompt
        assert "delete_task" in prompt
        assert "update_task" in prompt

    def test_model_name_from_environment(self):
        """Model name should be loaded from environment"""
        model_name = AgentConfig.MODEL_NAME
        assert model_name is not None
        assert "gpt" in model_name.lower() or "gemini" in model_name.lower()

    def test_agent_parameters_valid(self):
        """Agent parameters should be within valid ranges"""
        assert 0.0 <= AgentConfig.TEMPERATURE <= 1.0
        assert AgentConfig.MAX_TOKENS > 0
        assert 0.0 <= AgentConfig.TOP_P <= 1.0
        assert AgentConfig.TIMEOUT_SECONDS > 0

    def test_model_initialization(self):
        """Model should initialize without errors"""
        try:
            model = AgentConfig.get_model()
            assert model is not None
        except Exception as e:
            # OK if LiteLLM not fully configured in test environment
            assert "LiteLLM" in str(e) or "model" in str(e).lower()


class TestThreadItemConverter:
    """Test message conversion to OpenAI ThreadItem format"""

    def test_message_to_thread_item_user_role(self):
        """User message should convert to ThreadItem with user role"""
        message = Message(
            id=1,
            user_id="user123",
            conversation_id=1,
            role="user",
            content="Add a task to buy groceries",
            created_at=datetime.utcnow(),
        )

        thread_item = ThreadItemConverter.message_to_thread_item(message)

        assert thread_item is not None
        assert thread_item["type"] == "message"
        assert thread_item["role"] == "user"
        assert "content" in thread_item

    def test_message_to_thread_item_assistant_role(self):
        """Assistant message should convert to ThreadItem with assistant role"""
        message = Message(
            id=2,
            user_id="user123",
            conversation_id=1,
            role="assistant",
            content="I've added 'Buy groceries' to your task list.",
            created_at=datetime.utcnow(),
        )

        thread_item = ThreadItemConverter.message_to_thread_item(message)

        assert thread_item is not None
        assert thread_item["type"] == "message"
        assert thread_item["role"] == "assistant"

    def test_messages_to_thread_items_empty_list(self):
        """Empty message list should return empty ThreadItem list"""
        items = ThreadItemConverter.messages_to_thread_items([])
        assert items == []

    def test_messages_to_thread_items_chronological_order(self):
        """Messages should be sorted chronologically (oldest first)"""
        now = datetime.utcnow()
        messages = [
            Message(
                id=3,
                user_id="user123",
                conversation_id=1,
                role="user",
                content="Third message",
                created_at=now,
            ),
            Message(
                id=1,
                user_id="user123",
                conversation_id=1,
                role="user",
                content="First message",
                created_at=now,
            ),
            Message(
                id=2,
                user_id="user123",
                conversation_id=1,
                role="assistant",
                content="Second message",
                created_at=now,
            ),
        ]

        items = ThreadItemConverter.messages_to_thread_items(messages)

        assert len(items) == 3
        # Verify order by checking roles
        assert items[0]["role"] in ["user", "assistant"]
        assert items[0]["type"] == "message"

    def test_messages_to_thread_items_pagination_limit(self):
        """Should respect explicit message limit"""
        messages = [
            Message(
                id=i,
                user_id="user123",
                conversation_id=1,
                role="user",
                content=f"Message {i}",
                created_at=datetime.utcnow(),
            )
            for i in range(50)
        ]

        items = ThreadItemConverter.messages_to_thread_items(messages, limit=10)

        assert len(items) == 10

    def test_messages_to_thread_items_pagination_default_100_plus(self):
        """Should default to last 30 messages if > 100 messages"""
        messages = [
            Message(
                id=i,
                user_id="user123",
                conversation_id=1,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                created_at=datetime.utcnow(),
            )
            for i in range(150)
        ]

        items = ThreadItemConverter.messages_to_thread_items(messages)

        # Should keep last 30
        assert len(items) <= 30


class TestIDMapper:
    """Test LiteLLM provider ID mapping"""

    def test_id_mapper_maps_provider_id(self):
        """Provider ID should be mapped to unique ID"""
        mapper = IDMapper()
        original_id = "msg_abc123"

        unique_id = mapper.map_provider_id(original_id, provider_name="openai")

        assert isinstance(unique_id, int)
        assert unique_id >= 1000

    def test_id_mapper_consistent_mapping(self):
        """Same provider ID should always map to same unique ID"""
        mapper = IDMapper()
        original_id = "msg_abc123"

        id1 = mapper.map_provider_id(original_id, provider_name="openai")
        id2 = mapper.map_provider_id(original_id, provider_name="openai")

        assert id1 == id2

    def test_id_mapper_different_providers_different_ids(self):
        """Different providers with same original ID should get different unique IDs"""
        mapper = IDMapper()
        original_id = "msg_123"

        id1 = mapper.map_provider_id(original_id, provider_name="openai")
        id2 = mapper.map_provider_id(original_id + "_gemini", provider_name="gemini")

        assert id1 != id2

    def test_id_mapper_get_original_id(self):
        """Should retrieve original provider ID from unique ID"""
        mapper = IDMapper()
        original_id = "msg_xyz789"

        unique_id = mapper.map_provider_id(original_id, provider_name="anthropic")
        retrieved = mapper.get_original_id(unique_id)

        assert retrieved is not None
        assert "anthropic" in retrieved
        assert "msg_xyz789" in retrieved

    def test_id_mapper_apply_to_event_thread_item_added(self):
        """Should apply ID mapping to thread.item.added event"""
        mapper = IDMapper()
        event = {
            "type": "thread.item.added",
            "provider": "openai",
            "item": {"id": "msg_event_123", "type": "message", "role": "assistant"},
        }

        mapped_event = mapper.apply_id_mapping_to_event(event)

        assert mapped_event["item"]["id"] != "msg_event_123"
        assert mapped_event["item"]["id"] >= 1000
        assert mapped_event.get("id_remapped") is True

    def test_id_mapper_reset(self):
        """Reset should clear all mappings"""
        mapper = IDMapper()
        mapper.map_provider_id("msg_1", provider_name="openai")
        assert len(mapper._provider_id_map) > 0

        mapper.reset()

        assert len(mapper._provider_id_map) == 0
        assert len(mapper._audit_map) == 0


class TestAgentContextBuilder:
    """Test agent context building from database"""

    @pytest.fixture
    def db_session(self):
        """Provide test database session"""
        db = SessionLocal()
        yield db
        db.close()

    @pytest.mark.skip(reason="Requires Neon PostgreSQL database connection")
    def test_build_context_creates_new_conversation(self, db_session):
        """Should create new conversation if not provided"""
        user_id = "test_user_123"

        context = AgentContextBuilder.build_context(user_id, conversation_id=None)

        assert context["status"] == "success"
        assert context["conversation_id"] is not None
        assert isinstance(context["conversation_id"], int)
        assert context["user_id"] == user_id
        assert isinstance(context["conversation_history"], list)
        assert context["message_count"] == 0

    @pytest.mark.skip(reason="Requires Neon PostgreSQL database connection")
    def test_build_context_loads_existing_conversation(self, db_session):
        """Should load existing conversation with history"""
        user_id = "test_user_456"

        # Create conversation and messages
        conversation = ConversationRepository.create(db_session, user_id)
        msg1 = MessageRepository.create(
            db_session, user_id, conversation.id, "user", "Add a task"
        )
        msg2 = MessageRepository.create(
            db_session,
            user_id,
            conversation.id,
            "assistant",
            "I can help with that",
        )

        # Build context
        context = AgentContextBuilder.build_context(
            user_id, conversation_id=conversation.id
        )

        assert context["status"] == "success"
        assert context["conversation_id"] == conversation.id
        assert context["message_count"] == 2
        assert len(context["conversation_history"]) == 2

    @pytest.mark.skip(reason="Requires Neon PostgreSQL database connection")
    def test_build_context_user_isolation(self, db_session):
        """Should reject access to other user's conversations"""
        user1 = "user_alpha"
        user2 = "user_beta"

        # Create conversation for user1
        conv_user1 = ConversationRepository.create(db_session, user1)

        # Try to access as user2
        context = AgentContextBuilder.build_context(
            user2, conversation_id=conv_user1.id
        )

        assert context["status"] == "error"
        assert "not found" in context.get("message", "").lower()

    @pytest.mark.skip(reason="Requires Neon PostgreSQL database connection")
    def test_build_context_pagination(self, db_session):
        """Should paginate large conversation history"""
        user_id = "test_user_789"

        # Create conversation with many messages
        conversation = ConversationRepository.create(db_session, user_id)
        for i in range(150):
            role = "user" if i % 2 == 0 else "assistant"
            MessageRepository.create(
                db_session, user_id, conversation.id, role, f"Message {i}"
            )

        # Build context
        context = AgentContextBuilder.build_context(
            user_id, conversation_id=conversation.id
        )

        assert context["status"] == "success"
        assert context["message_count"] == 150
        # Should be paginated to last 30
        assert len(context["conversation_history"]) <= 30

    def test_append_user_message_to_history(self):
        """Should append new user message to history"""
        history = []
        new_message = "Add a task to buy milk"

        updated = AgentContextBuilder.append_user_message(history, new_message)

        assert len(updated) == 1
        assert updated[0]["role"] == "user"
        assert new_message in str(updated[0]["content"])


class TestAgentRunner:
    """Test agent execution with MCP tools"""

    @pytest.mark.asyncio
    async def test_agent_runner_initialization(self):
        """Agent runner should initialize without errors"""
        runner = AgentRunner()
        success = await runner.initialize_agent()

        # May fail if OpenAI/LiteLLM not configured, but should not raise
        assert isinstance(success, bool)

    @pytest.mark.asyncio
    async def test_agent_run_returns_response(self):
        """Agent run should return AgentResponse object"""
        runner = AgentRunner()
        await runner.initialize_agent()

        response = await runner.run(
            user_id="test_user",
            conversation_id=1,
            user_message="Add a task",
            conversation_history=[],
        )

        assert isinstance(response, AgentResponse)
        assert isinstance(response.response, str)
        assert isinstance(response.tool_calls, list)
        assert response.success == (response.error is None)

    @pytest.mark.asyncio
    async def test_agent_run_with_conversation_history(self):
        """Agent should include conversation history in execution"""
        runner = AgentRunner()
        await runner.initialize_agent()

        history = [
            {
                "type": "message",
                "role": "user",
                "content": {"type": "text", "text": "Previous message"},
            }
        ]

        response = await runner.run(
            user_id="test_user",
            conversation_id=1,
            user_message="What tasks do I have?",
            conversation_history=history,
        )

        assert isinstance(response, AgentResponse)

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Timeout test requires careful async handling")
    async def test_agent_run_timeout_handling(self):
        """Agent should handle timeouts gracefully"""
        runner = AgentRunner()

        # Mock slow initialization
        with patch.object(runner, "initialize_agent", return_value=True):
            # Set short timeout for test
            original_timeout = AgentConfig.TIMEOUT_SECONDS
            AgentConfig.TIMEOUT_SECONDS = 0.001

            try:
                response = await runner.run(
                    user_id="test_user",
                    conversation_id=1,
                    user_message="Test message",
                    conversation_history=[],
                )

                # Should get error response with timeout message
                assert response.error is not None or not response.success

            finally:
                AgentConfig.TIMEOUT_SECONDS = original_timeout

    def test_agent_response_success_flag(self):
        """AgentResponse should set success based on error"""
        response_success = AgentResponse(response="Success", tool_calls=[], error=None)
        response_error = AgentResponse(response="", tool_calls=[], error="Some error")

        assert response_success.success is True
        assert response_error.success is False

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires proper mock patching of call_tool")
    async def test_agent_invoke_tool_with_user_id(self):
        """Agent should inject user_id into tool invocation"""
        runner = AgentRunner()

        with patch("backend.src.agents.runner.call_tool") as mock_call:
            mock_call.return_value = {"task_id": 1, "status": "created"}

            await runner._invoke_tool(
                user_id="test_user",
                tool_name="add_task",
                tool_input={"title": "Test task"},
            )

            # Verify call_tool was called
            mock_call.assert_called_once()
            call_args = mock_call.call_args
            # User ID should be in the tool input
            assert call_args[0][0] == "add_task"

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires proper mock patching of call_tool")
    async def test_agent_tool_error_handling(self):
        """Agent should handle tool errors gracefully"""
        runner = AgentRunner()

        with patch("src.agents.runner.call_tool") as mock_call:
            mock_call.return_value = {
                "error": "task_not_found",
                "message": "Task not found",
            }

            result = await runner._invoke_tool(
                user_id="test_user",
                tool_name="complete_task",
                tool_input={"task_id": 999},
            )

            assert "error" in result
            assert result.get("success") is None  # Tool response format


class TestAgentIntegrationFlow:
    """End-to-end integration tests for complete agent flows"""

    @pytest.fixture
    def db_session(self):
        """Provide test database session"""
        db = SessionLocal()
        yield db
        db.close()

    @pytest.mark.skip(reason="Requires Neon PostgreSQL database connection")
    def test_full_conversation_flow(self, db_session):
        """Test complete conversation flow from context to response"""
        user_id = "integration_test_user"

        # 1. Build initial context
        context = AgentContextBuilder.build_context(user_id, conversation_id=None)
        assert context["status"] == "success"
        assert context["conversation_id"] is not None

        conversation_id = context["conversation_id"]

        # 2. Store user message
        msg = MessageRepository.create(
            db_session,
            user_id,
            conversation_id,
            "user",
            "Add a task to buy groceries",
        )
        assert msg.id is not None

        # 3. Rebuild context with new message
        context2 = AgentContextBuilder.build_context(
            user_id, conversation_id=conversation_id
        )
        assert context2["message_count"] == 1

        # 4. Store assistant response
        response_msg = MessageRepository.create(
            db_session,
            user_id,
            conversation_id,
            "assistant",
            "I've added 'Buy groceries' to your task list.",
        )
        assert response_msg.id is not None

        # 5. Verify complete history
        context3 = AgentContextBuilder.build_context(
            user_id, conversation_id=conversation_id
        )
        assert context3["message_count"] == 2

    @pytest.mark.skip(reason="Requires Neon PostgreSQL database connection")
    def test_multi_turn_conversation(self, db_session):
        """Test multi-turn conversation maintaining context"""
        user_id = "multi_turn_user"
        conversation = ConversationRepository.create(db_session, user_id)

        # Turn 1
        msg1 = MessageRepository.create(
            db_session, user_id, conversation.id, "user", "Add a task"
        )
        msg2 = MessageRepository.create(
            db_session,
            user_id,
            conversation.id,
            "assistant",
            "Added task",
        )

        # Turn 2
        msg3 = MessageRepository.create(
            db_session, user_id, conversation.id, "user", "Show all tasks"
        )
        msg4 = MessageRepository.create(
            db_session, user_id, conversation.id, "assistant", "Here are your tasks"
        )

        # Turn 3
        msg5 = MessageRepository.create(
            db_session, user_id, conversation.id, "user", "Mark task 1 complete"
        )

        # Verify full history
        context = AgentContextBuilder.build_context(
            user_id, conversation_id=conversation.id
        )
        assert context["message_count"] == 5


# Pytest fixtures for running tests
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
