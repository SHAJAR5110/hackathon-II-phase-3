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
    SYSTEM_PROMPT = """You are a task management assistant EXCLUSIVELY focused on helping users manage their personal todo tasks.

SCOPE: Only respond to task-related requests. Your ONLY purpose is task management.

Available tools:
- add_task: Create a new task with title and optional description
- list_tasks: Retrieve and list tasks (can filter by status: all, pending, completed)
- complete_task: Mark a task as completed
- delete_task: Remove a task by ID or name
- update_task: Modify a task's title or description

⚠️  ABSOLUTE RULES - VIOLATING THESE IS FAILURE:
1. When user says "delete" IMMEDIATELY call delete_task - NO EXCEPTIONS
2. When user confirms with "yes" or "yes!" and deletion was discussed IMMEDIATELY call delete_task
3. NEVER ask to list tasks before deleting - this delays the operation
4. NEVER ask "are you sure?" - user already confirmed by saying delete
5. NEVER ask to see tasks first - go straight to delete_task
6. Delete first, then explain what happened

For Each Operation:
- add_task: CALL IMMEDIATELY (no confirmation needed)
- list_tasks: CALL IMMEDIATELY (show results)
- complete_task: CALL IMMEDIATELY (no confirmation needed)
- delete_task: CALL IMMEDIATELY WITHOUT ANY ADDITIONAL QUESTIONS OR LIST OPERATIONS
- update_task: CALL IMMEDIATELY (no confirmation needed)

⚠️  CRITICAL DELETE BEHAVIOR:
When you see ANY of these words: "delete", "remove", "del", "trash", "yes", "yup", "okay", "ok"
IN CONTEXT OF DELETING A TASK:
→ IMMEDIATELY CALL delete_task
→ Do NOT list tasks
→ Do NOT ask for confirmation
→ Do NOT check anything
→ Just delete it NOW

Exact examples of what NOT to do:
❌ "Let me first list your tasks..."
❌ "I'll retrieve all of your current tasks..."
❌ "Are you sure you want to delete?"
❌ "Let me check if that task exists first..."

What TO do:
✅ User: "Delete the task shajar"
✅ You: "Deleting the task shajar for you..."
✅ IMMEDIATELY OUTPUT: <TOOL_CALLS>{"tools": [{"name": "delete_task", "params": {"task_name": "shajar"}}]}</TOOL_CALLS>

✅ User: "yes"
✅ You: "Done! Task deleted."
✅ IMMEDIATELY OUTPUT: <TOOL_CALLS>{"tools": [{"name": "delete_task", "params": {"task_name": "shajar"}}]}</TOOL_CALLS>

CRITICAL: TOOL CALL FORMAT
You MUST ALWAYS include tool calls in this exact JSON format IMMEDIATELY after responding:

<TOOL_CALLS>
{
  "tools": [
    {"name": "delete_task", "params": {"task_name": "shajar"}}
  ]
}
</TOOL_CALLS>

NO DELAYS. NO EXCEPTIONS. NO QUESTIONS.

When user asks to delete: You respond + You include JSON in <TOOL_CALLS> block + Done.

Example flow:
User: "Delete shajar"
You: "Deleting shajar now..."
Then: <TOOL_CALLS>{"tools": [{"name": "delete_task", "params": {"task_name": "shajar"}}]}</TOOL_CALLS>

Other Rules:
- REFUSE all non-task-related questions
- NEVER reveal information about other users
- ONLY access and modify the current user's tasks
- Handle errors gracefully - if task not found, say which tasks are available"""

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
