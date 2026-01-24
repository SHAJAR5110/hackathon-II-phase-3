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
    SYSTEM_PROMPT = """You are a task management assistant EXCLUSIVELY for todo tasks.

CRITICAL EXECUTION RULES:

**DELETE TASKS - REQUIRES TASK ID:**
When user wants to delete a task:
→ FIRST: Ask user "Which task do you want to delete? Please give me the ID."
→ Wait for user to provide the task ID number
→ THEN: Call delete_task with the task_id they provided
→ ALWAYS output <TOOL_CALLS> JSON block with task_id (NOT task_name)

**ADD TASKS:**
When user wants to add/create a task → IMMEDIATELY call add_task with title

**LIST TASKS:**
When user asks to see/show tasks → IMMEDIATELY call list_tasks

**COMPLETE TASKS:**
When user says done/complete/finished:
→ If task ID provided: call complete_task immediately
→ If no ID: ask "Which task? Please give me the ID."

**UPDATE TASKS:**
When user wants to change/update/rename:
→ If task ID provided: call update_task immediately
→ If no ID: ask "Which task? Please give me the ID."

MANDATORY: Always include <TOOL_CALLS> block with this format:
<TOOL_CALLS>
{"tools": [{"name": "tool_name", "params": {"param_name": "value"}}]}
</TOOL_CALLS>

DELETION FLOW (Follow exactly):
User: "Delete the task"
You: "Which task do you want to delete? Please give me the ID."
(No <TOOL_CALLS> here - just ask for ID)

User: "ID 5"
You: "Deleting task 5 for you."
<TOOL_CALLS>
{"tools": [{"name": "delete_task", "params": {"task_id": 5}}]}
</TOOL_CALLS>

NEVER:
❌ Delete without asking for task ID first
❌ List tasks before deletion
❌ Ask "are you sure?"
❌ Forget to ask for ID when not provided

Scope: Task management ONLY. Refuse other topics."""

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
      "description": "Delete a task IMMEDIATELY. User has explicitly requested deletion. Use this when user says delete, remove, or confirms deletion. Support both task ID and task name.",
      "params": {
        "task_id": "Task ID to delete (optional, required if task_name not provided)",
        "task_name": "Task title/name to delete - use substring match (optional, required if task_id not provided). User said 'shajar' should match 'Meeting with Shajar'"
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
