"""
Agent Configuration Module
Configures the Groq Agent with system prompt, model selection, and parameters
"""

import os
from typing import Optional

from ..logging_config import get_logger
from .models_adapter import LiteLLMModelAdapter

logger = get_logger(__name__)


class AgentConfig:
    """Configuration for the Groq AI Agent"""

    # System prompt for the agent
    SYSTEM_PROMPT = """You are a helpful task management assistant powered by Groq AI. Help users manage their todo tasks using natural language.

Available tools:
- add_task: Create a new task with title and optional description
- list_tasks: Retrieve and list tasks (can filter by status: all, pending, completed)
- complete_task: Mark a task as completed
- delete_task: Remove a task
- update_task: Modify a task's title or description

Instructions:
1. When users mention adding/creating/remembering something, use add_task
2. When users ask to see/show/list tasks, use list_tasks with appropriate filter
3. When users say done/complete/finished, use complete_task
4. When users say delete/remove/cancel, use delete_task
5. When users say change/update/rename, use update_task
6. Always confirm actions with friendly responses
7. Handle errors gracefully - if a task is not found, ask for clarification
8. Be conversational and helpful
9. When ambiguous, ask clarifying questions before taking action
10. Use the reasoning capabilities to understand complex requests"""

    # Groq Model Configuration
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    """Groq model to use (openai/gpt-oss-120b with extended thinking)"""

    # Agent parameters for Groq
    TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "1.0"))
    """Temperature for response generation (0.0-1.0)"""

    MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "8192"))
    """Maximum tokens in response"""

    TOP_P: float = float(os.getenv("GROQ_TOP_P", "1.0"))
    """Top-p sampling parameter for diversity"""

    REASONING_EFFORT: str = os.getenv("GROQ_REASONING_EFFORT", "medium")
    """Reasoning effort level (low, medium, high)"""

    TIMEOUT_SECONDS: int = int(os.getenv("AGENT_TIMEOUT", "30"))
    """Timeout for agent execution"""

    @classmethod
    def get_tool_schema(cls) -> str:
        """
        Get the tool schema for structured prompting

        Returns:
            str: JSON schema for available tools
        """
        return """{
  "tools": [
    {
      "name": "add_task",
      "description": "Create a new task",
      "params": {
        "title": "Task title (required)",
        "description": "Task description (optional)"
      }
    },
    {
      "name": "list_tasks",
      "description": "Get tasks with optional status filter",
      "params": {
        "status": "Filter status - 'all', 'pending', or 'completed' (default: 'all')"
      }
    },
    {
      "name": "complete_task",
      "description": "Mark a task as completed",
      "params": {
        "task_id": "Task ID to complete (required)"
      }
    },
    {
      "name": "delete_task",
      "description": "Delete a task",
      "params": {
        "task_id": "Task ID to delete (required)"
      }
    },
    {
      "name": "update_task",
      "description": "Update a task's title or description",
      "params": {
        "task_id": "Task ID to update (required)",
        "title": "New title (optional)",
        "description": "New description (optional)"
      }
    }
  ]
}"""

    @classmethod
    def get_system_prompt(cls) -> str:
        """
        Get the system prompt for the agent

        Returns:
            str: System prompt text
        """
        return cls.SYSTEM_PROMPT

    @classmethod
    def get_model(cls) -> LiteLLMModelAdapter:
        """
        Get configured LiteLLM model instance (for backwards compatibility)

        Returns:
            LiteLLMModelAdapter: Configured model for agent
        """
        try:
            model = LiteLLMModelAdapter(
                model_id=cls.GROQ_MODEL,
                temperature=cls.TEMPERATURE,
                max_tokens=cls.MAX_TOKENS,
                top_p=cls.TOP_P,
            )
            logger.info(
                "agent_model_initialized",
                model_name=cls.GROQ_MODEL,
                temperature=cls.TEMPERATURE,
            )
            return model
        except Exception as e:
            logger.error("agent_model_initialization_failed", error=str(e))
            raise


__all__ = ["AgentConfig"]
