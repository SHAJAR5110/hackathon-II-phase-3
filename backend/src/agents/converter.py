"""
ThreadItemConverter Module
Converts database Message objects to OpenAI SDK ThreadItem format
Handles conversation history for the agent
"""

from typing import List, Optional

from ..logging_config import get_logger
from ..models import Message
from .models_adapter import ThreadItemAdapter

logger = get_logger(__name__)


class ThreadItemConverter:
    """Convert database Message objects to OpenAI ThreadItem format"""

    @staticmethod
    def message_to_thread_item(message: Message) -> dict:
        """
        Convert a single Message ORM object to ThreadItem format

        Parameters:
            message (Message): Database message object with id, role, content, created_at

        Returns:
            dict: Formatted message for OpenAI agent

        Example:
            Message(id=1, role="user", content="Add a task", created_at=...) →
            {"type": "message", "role": "user", "content": {"type": "text", "text": "Add a task"}}
        """
        try:
            # Create ThreadItem with proper OpenAI format
            thread_item = ThreadItemAdapter.create_message_item(
                type="message",
                role=message.role,  # "user" or "assistant"
                content=message.content,
            )

            logger.debug(
                "message_converted_to_thread_item",
                message_id=message.id,
                role=message.role,
                content_length=len(message.content),
            )

            return thread_item

        except Exception as e:
            logger.error(
                "message_conversion_failed",
                message_id=message.id,
                error=str(e),
            )
            raise

    @staticmethod
    def messages_to_thread_items(
        messages: List[Message], limit: Optional[int] = None
    ) -> List[dict]:
        """
        Convert a list of Message objects to ThreadItem format
        Maintains chronological order (oldest first)
        Supports pagination for large histories

        Parameters:
            messages (List[Message]): List of database message objects
            limit (Optional[int]): Maximum number of messages to include.
                                   If messages exceed limit, keep last N messages
                                   (default: None = include all)

        Returns:
            List[dict]: Messages in chronological order ready for agent

        Notes:
            - Messages are sorted by created_at (oldest first)
            - If history > 100 messages, default to last 30 for context window
            - All messages must be from same conversation_id (assumed valid)
        """
        if not messages:
            logger.debug("no_messages_to_convert")
            return []

        # Sort messages by created_at (oldest first)
        sorted_messages = sorted(messages, key=lambda m: m.created_at)

        # Apply pagination if needed
        if limit is None:
            # Default: if more than 100 messages, keep last 30
            if len(sorted_messages) > 100:
                limit = 30
                logger.info(
                    "messages_paginated",
                    total_messages=len(sorted_messages),
                    kept_messages=limit,
                )
                # Keep the last `limit` messages
                sorted_messages = sorted_messages[-limit:]
        elif limit > 0:
            # Apply explicit limit - keep last N messages
            if len(sorted_messages) > limit:
                logger.info(
                    "messages_paginated",
                    total_messages=len(sorted_messages),
                    kept_messages=limit,
                )
                sorted_messages = sorted_messages[-limit:]

        # Convert each message to ThreadItem
        thread_items: List[dict] = []
        for message in sorted_messages:
            try:
                thread_item = ThreadItemConverter.message_to_thread_item(message)
                thread_items.append(thread_item)
            except Exception as e:
                logger.error(
                    "failed_to_convert_message_in_batch",
                    message_id=message.id,
                    error=str(e),
                )
                # Continue with other messages, don't fail entire batch
                continue

        logger.info(
            "messages_converted_to_thread_items",
            total_converted=len(thread_items),
            total_input=len(messages),
        )

        return thread_items


__all__ = ["ThreadItemConverter"]
