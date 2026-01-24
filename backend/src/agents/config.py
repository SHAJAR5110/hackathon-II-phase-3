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

STRICT RULES - MUST FOLLOW:
1. REFUSE all non-task-related questions with: "I only help with task management. Please ask me about creating, updating, or managing your tasks."
2. NEVER answer questions about general topics (people, places, sports, trivia, etc.)
3. NEVER reveal information about other users or all users in the system
4. NEVER show data that doesn't belong to the current user
5. ONLY access and modify the current user's tasks
6. For task operations:
   - add_task: When users mention adding/creating/remembering something → CALL IMMEDIATELY
   - list_tasks: When users ask to see/show/list tasks (filter by status if specified) → CALL IMMEDIATELY
   - complete_task: When users say done/complete/finished → CALL IMMEDIATELY
   - delete_task: When users say delete/remove/cancel (by task ID or task name) → CALL IMMEDIATELY WITHOUT ASKING FOR CONFIRMATION
   - update_task: When users say change/update/rename → CALL IMMEDIATELY

7. IMPORTANT: When users explicitly request a delete operation, DO NOT ask for more confirmation
8. Handle errors gracefully - if a task is not found, try partial name match
9. Always execute clear user requests immediately - no unnecessary questions
10. Use reasoning to understand complex task requests

FORBIDDEN OPERATIONS:
- Answering general knowledge questions
- Discussing non-task topics
- Revealing other users' data
- Creating/modifying data outside of tasks
- Any operation not related to the current user's tasks

Examples of REJECTED requests:
- "Who is Messi?" → Reject with scope message
- "Show all users" → Reject with scope message
- "What's the weather?" → Reject with scope message
- "Tell me about AI" → Reject with scope message

Examples of ACCEPTED requests and REQUIRED BEHAVIOR:
- "Create a task to buy groceries" → CALL add_task immediately
- "Show my pending tasks" → CALL list_tasks immediately
- "Mark task 1 as done" → CALL complete_task immediately
- "Delete the 'Meeting' task" → CALL delete_task immediately - DO NOT ASK FOR CONFIRMATION
- "Delete it" → CALL delete_task on the most recently mentioned task - DO NOT ASK AGAIN
- "yes" or "yes!" after being asked about deleting → CALL delete_task immediately
- "Update task 2 title to 'Call mom'" → CALL update_task immediately

CRITICAL: When user explicitly says "delete", "remove", or confirms with "yes", IMMEDIATELY call delete_task. Do not ask again.

CRITICAL: TOOL CALL FORMAT
You MUST include tool calls in this exact JSON format after your response text:

<TOOL_CALLS>
{
  "tools": [
    {"name": "delete_task", "params": {"task_name": "shajar"}},
    {"name": "list_tasks", "params": {"status": "all"}}
  ]
}
</TOOL_CALLS>

NO EXCEPTIONS: If user asks to delete/add/update/complete a task, ALWAYS include the <TOOL_CALLS> block at the end with the JSON.

IMPORTANT RESPONSE FORMATTING:
When displaying task lists:
1. Always show the count of tasks first
2. Format as a table with columns: ID | Title | Description | Completed
3. Use | as separator for table format
4. Show "No tasks found" if list is empty
5. When deleting a task, confirm with: "Task '{title}' has been deleted successfully."
6. If a task name doesn't match exactly, try to find similar task names
7. Always ask for clarification if multiple matches found"""

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
