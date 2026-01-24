"""
Model Adapter Module
Provides abstraction over LiteLLM and OpenAI agents for flexibility
In production, would use openai_agents.extensions.models.litellm_model
"""

from typing import Optional

from ..logging_config import get_logger

logger = get_logger(__name__)


class LiteLLMModelAdapter:
    """
    Adapter for LiteLLM model initialization
    Provides abstraction over openai-agents dependencies
    """

    def __init__(
        self,
        model_id: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        top_p: float = 0.9,
        **kwargs,
    ):
        """
        Initialize LiteLLM model adapter

        Parameters:
            model_id (str): Model identifier (e.g., "openai/gpt-4o", "gemini/gemini-2.0-flash")
            temperature (float): Temperature for generation (0.0-1.0)
            max_tokens (int): Maximum tokens in response
            top_p (float): Top-p sampling parameter
            **kwargs: Additional parameters for model configuration
        """
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.kwargs = kwargs

        logger.info(
            "litellm_model_adapter_initialized",
            model_id=model_id,
            temperature=temperature,
        )

    def to_dict(self) -> dict:
        """Convert to configuration dictionary"""
        return {
            "model_id": self.model_id,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            **self.kwargs,
        }


class ThreadItemAdapter:
    """
    Adapter for OpenAI ThreadItem format
    Abstracts thread item creation for flexibility
    """

    @staticmethod
    def create_message_item(
        type: str = "message",
        role: str = "user",
        content: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """
        Create a ThreadItem for a message

        Parameters:
            type (str): Item type (usually "message")
            role (str): Message role ("user" or "assistant")
            content (str or dict): Message content
            **kwargs: Additional item properties

        Returns:
            dict: ThreadItem in OpenAI format
        """
        item = {
            "type": type,
            "role": role,
        }

        # Handle content as string or structured block
        if isinstance(content, str):
            item["content"] = {"type": "text", "text": content}
        elif isinstance(content, dict):
            item["content"] = content
        else:
            item["content"] = {"type": "text", "text": str(content)}

        item.update(kwargs)
        return item

    @staticmethod
    def create_text_block(text: str) -> dict:
        """
        Create a TextContentBlock

        Parameters:
            text (str): Text content

        Returns:
            dict: TextContentBlock representation
        """
        return {"type": "text", "text": text}


__all__ = ["LiteLLMModelAdapter", "ThreadItemAdapter"]
