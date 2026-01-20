"""
Agent Context Builder Module
Builds conversation context from database for stateless agent execution
Reconstructs message history per-request
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..logging_config import get_logger
from ..models import Message
from ..repositories import ConversationRepository, MessageRepository
from .converter import ThreadItemConverter

logger = get_logger(__name__)


class AgentContextBuilder:
    """Build conversation context from database for stateless agent operations"""

    @staticmethod
    def build_context(
        user_id: str,
        conversation_id: Optional[int] = None,
        message_limit: Optional[int] = None,
    ) -> Dict:
        """
        Build complete conversation context from database

        This method implements stateless operation by:
        1. Loading conversation from database (or creating new one)
        2. Loading all messages for conversation
        3. Converting to ThreadItem format for agent
        4. Including user_id for tool access

        IMPORTANT - ASYNC/SYNC PATTERN:
        This method is synchronous (not async) but is called from async routes
        (e.g., POST /api/{user_id}/chat). This is intentional and acceptable because:
        
        1. SQLAlchemy ORM operations are synchronous (not async-native)
        2. Database operations are fast for reasonable message counts
        3. Used within FastAPI async context manager but doesn't await
        4. FastAPI middleware stack allows sync functions in async context
        
        Future optimization (Phase 7):
        - Switch to async SQLAlchemy (SQLModel with asyncpg driver)
        - Use: async with AsyncSession() as db
        - Make this method async with await db.execute()
        - Run: response = await self.build_context(...)
        
        Current approach is acceptable for Phase 6 with typical message counts (< 100).
        Performance will be monitored; optimize if latency exceeds SLA.

        Parameters:
            user_id (str): The authenticated user ID
            conversation_id (Optional[int]): Existing conversation ID (creates new if not provided)
            message_limit (Optional[int]): Max messages to include in history (pagination)

        Returns:
            dict: Context ready for agent execution
            {
                "conversation_id": int,
                "user_id": str,
                "conversation_history": List[ThreadItem],
                "message_count": int,
                "status": "success" | "error"
            }

        Raises:
            Exception: If database operations fail
        """
        db: Session = SessionLocal()
        result_conversation_id = conversation_id
        try:
            # Load or create conversation
            if conversation_id:
                conversation = ConversationRepository.read(db, user_id, conversation_id)
                if not conversation:
                    logger.warning(
                        "conversation_not_found",
                        user_id=user_id,
                        conversation_id=conversation_id,
                    )
                    return {
                        "status": "error",
                        "message": "Conversation not found",
                        "conversation_id": None,
                        "user_id": user_id,
                        "conversation_history": [],
                        "message_count": 0,
                    }
            else:
                # Create new conversation (stateless per-request)
                conversation = ConversationRepository.create(db, user_id)
                logger.info(
                    "new_conversation_created",
                    user_id=user_id,
                    conversation_id=conversation.id,
                )

            result_conversation_id = conversation.id

            # Load all messages for conversation (with user_id filter for security)
            messages: List[Message] = MessageRepository.list_by_conversation(
                db, conversation.id, user_id=user_id
            )

            logger.info(
                "messages_loaded_from_database",
                user_id=user_id,
                conversation_id=conversation.id,
                message_count=len(messages),
            )

            # Convert to ThreadItem format using converter
            conversation_history = ThreadItemConverter.messages_to_thread_items(
                messages, limit=message_limit
            )

            logger.info(
                "conversation_context_built",
                user_id=user_id,
                conversation_id=conversation.id,
                total_messages=len(messages),
                context_messages=len(conversation_history),
            )

            return {
                "status": "success",
                "conversation_id": conversation.id,
                "user_id": user_id,
                "conversation_history": conversation_history,
                "message_count": len(messages),
            }

        except Exception as e:
            logger.error(
                "context_builder_failed",
                user_id=user_id,
                conversation_id=result_conversation_id,
                error=str(e),
            )
            return {
                "status": "error",
                "message": "Failed to build context",
                "conversation_id": result_conversation_id,
                "user_id": user_id,
                "conversation_history": [],
                "message_count": 0,
            }

        finally:
            db.close()

    @staticmethod
    def append_user_message(
        conversation_history: List[dict], user_message: str
    ) -> List[dict]:
        """
        Append new user message to conversation history

        Parameters:
            conversation_history (List[dict]): Existing conversation history
            user_message (str): New message from user

        Returns:
            List[dict]: Updated history with new message appended
        """
        try:
            from .models_adapter import ThreadItemAdapter

            # Create ThreadItem for user message
            new_item = ThreadItemAdapter.create_message_item(
                type="message",
                role="user",
                content=user_message,
            )

            # Append to history
            updated_history = (
                conversation_history.copy() if conversation_history else []
            )
            updated_history.append(new_item)

            logger.debug(
                "user_message_appended_to_history",
                total_messages=len(updated_history),
                message_length=len(user_message),
            )

            return updated_history

        except Exception as e:
            logger.error("failed_to_append_user_message", error=str(e))
            raise


__all__ = ["AgentContextBuilder"]
