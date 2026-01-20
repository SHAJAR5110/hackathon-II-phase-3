"""
Agent Configuration Module
Configures the OpenAI Agent with system prompt, model selection, and parameters
"""

import os
from typing import Optional

from ..logging_config import get_logger
from .models_adapter import LiteLLMModelAdapter

logger = get_logger(__name__)


class AgentConfig:
    """Configuration for the AI Agent"""

    # System prompt for the agent
    SYSTEM_PROMPT = """You are a helpful task management assistant. Help users manage their todo tasks using natural language.

Available tools:
- add_task: Create a new task
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
9. When ambiguous, ask clarifying questions before taking action"""

    # Model configuration
    MODEL_NAME: str = os.getenv("AGENT_MODEL", "openai/gpt-4o")
    """Model to use for the agent (supports OpenAI, Gemini, etc. via LiteLLM)"""

    # Agent parameters
    TEMPERATURE: float = 0.7
    """Temperature for response generation (0.0-1.0, lower = more deterministic)"""

    MAX_TOKENS: int = 4096
    """Maximum tokens in response"""

    TOP_P: float = 0.9
    """Top-p sampling parameter for diversity"""

    TIMEOUT_SECONDS: int = 30
    """Timeout for agent execution"""

    @classmethod
    def get_model(cls) -> LiteLLMModelAdapter:
        """
        Get configured LiteLLM model instance

        Returns:
            LiteLLMModelAdapter: Configured model for agent
        """
        try:
            model = LiteLLMModelAdapter(
                model_id=cls.MODEL_NAME,
                temperature=cls.TEMPERATURE,
                max_tokens=cls.MAX_TOKENS,
                top_p=cls.TOP_P,
            )
            logger.info(
                "agent_model_initialized",
                model_name=cls.MODEL_NAME,
                temperature=cls.TEMPERATURE,
            )
            return model
        except Exception as e:
            logger.error("agent_model_initialization_failed", error=str(e))
            raise

    @classmethod
    def get_system_prompt(cls) -> str:
        """
        Get the system prompt for the agent

        Returns:
            str: System prompt text
        """
        return cls.SYSTEM_PROMPT


__all__ = ["AgentConfig"]
