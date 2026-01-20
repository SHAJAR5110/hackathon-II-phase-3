"""
Chat Endpoint - Core interface for conversational task management
Implements POST /api/{user_id}/chat endpoint with full conversation orchestration
Feature: 1-chatbot-ai
"""

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from ..agents.config import AgentConfig
from ..agents.context import AgentContextBuilder
from ..agents.runner import AgentRunner
from ..db import SessionLocal
from ..logging_config import get_logger
from ..middleware.auth import get_current_user
from ..repositories import ConversationRepository, MessageRepository

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["chat"])


# ============================================================================
# Request/Response Models
# ============================================================================


class ChatRequest(BaseModel):
    """Chat endpoint request body"""

    conversation_id: Optional[int] = Field(
        default=None,
        description="Existing conversation ID (creates new if not provided)",
    )
    message: str = Field(..., min_length=1, max_length=4096, description="User message")


class ToolCall(BaseModel):
    """Tool invocation record"""

    tool: str = Field(..., description="Tool name")
    params: Dict[str, Any] = Field(..., description="Tool parameters")


class ChatResponse(BaseModel):
    """Chat endpoint response body"""

    conversation_id: int = Field(..., description="Conversation ID")
    response: str = Field(..., description="Assistant response")
    tool_calls: List[ToolCall] = Field(
        default_factory=list, description="Tools invoked"
    )


class ErrorResponse(BaseModel):
    """Error response body"""

    error: str = Field(..., description="Error message")
    request_id: str = Field(..., description="Request ID for traceability")


# ============================================================================
# Chat Endpoint
# ============================================================================


@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def chat_endpoint(
    user_id: str,
    request: Request,
    chat_request: ChatRequest,
    authenticated_user_id: str = Depends(get_current_user),
) -> ChatResponse:
    """
    Chat endpoint for conversational task management

    Orchestrates full conversation flow:
    1. Verify user_id matches authenticated user
    2. Load or create conversation
    3. Store user message
    4. Execute agent with conversation history
    5. Store assistant response
    6. Return formatted response

    Parameters:
        user_id (str): User ID from URL path
        request (Request): FastAPI request object
        chat_request (ChatRequest): Request body with message and optional conversation_id
        authenticated_user_id (str): Authenticated user ID from dependency

    Returns:
        ChatResponse: Conversation ID, assistant response, and tool calls

    Raises:
        HTTPException: 401 if user_id mismatch, 400 for invalid input, 500 for server errors
    """
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        # Step 1: Verify user_id matches authenticated user
        if user_id != authenticated_user_id:
            logger.warning(
                "User ID mismatch",
                path_user_id=user_id,
                auth_user_id=authenticated_user_id,
                request_id=request_id,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID mismatch",
            )

        logger.info(
            "chat_request_started",
            user_id=user_id,
            conversation_id=chat_request.conversation_id,
            message_length=len(chat_request.message),
            request_id=request_id,
        )

        # Step 2: Load or create conversation
        db = SessionLocal()
        try:
            conversation_id = await _handle_conversation_retrieval(
                db, user_id, chat_request.conversation_id, request_id
            )
            if not conversation_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve or create conversation",
                )

            # Step 3: Store user message
            await _store_user_message(
                db, user_id, conversation_id, chat_request.message, request_id
            )

            # Step 4: Build conversation context and execute agent
            agent_response = await _execute_agent(
                user_id, conversation_id, chat_request.message, request_id
            )

            if agent_response["error"]:
                logger.error(
                    "agent_execution_failed",
                    user_id=user_id,
                    conversation_id=conversation_id,
                    error=agent_response["error"],
                    request_id=request_id,
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=agent_response["response"],
                )

            # Step 5: Store assistant response
            await _store_assistant_response(
                db,
                user_id,
                conversation_id,
                agent_response["response"],
                agent_response["tool_calls"],
                request_id,
            )

            # Step 6: Format and return response
            response = await _format_response(
                conversation_id,
                agent_response["response"],
                agent_response["tool_calls"],
            )

            logger.info(
                "chat_request_completed",
                user_id=user_id,
                conversation_id=conversation_id,
                tool_calls_count=len(response.tool_calls),
                response_length=len(response.response),
                request_id=request_id,
            )

            return response

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "chat_endpoint_failed",
            user_id=user_id,
            error=str(e),
            error_type=type(e).__name__,
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# ============================================================================
# Helper Functions
# ============================================================================


async def _handle_conversation_retrieval(
    db, user_id: str, conversation_id: Optional[int], request_id: str
) -> Optional[int]:
    """
    Load existing conversation or create new one

    Parameters:
        db: Database session
        user_id (str): Authenticated user
        conversation_id (Optional[int]): Existing conversation ID
        request_id (str): Request ID for logging

    Returns:
        int: Conversation ID, or None if failed
    """
    try:
        if conversation_id:
            # Load existing conversation
            conversation = ConversationRepository.read(db, user_id, conversation_id)
            if not conversation:
                logger.warning(
                    "conversation_not_found_in_retrieval",
                    user_id=user_id,
                    conversation_id=conversation_id,
                    request_id=request_id,
                )
                return None

            logger.info(
                "conversation_loaded",
                user_id=user_id,
                conversation_id=conversation.id,
                request_id=request_id,
            )
            return conversation.id
        else:
            # Create new conversation
            conversation = ConversationRepository.create(db, user_id)
            logger.info(
                "conversation_created",
                user_id=user_id,
                conversation_id=conversation.id,
                request_id=request_id,
            )
            return conversation.id

    except Exception as e:
        logger.error(
            "conversation_retrieval_failed",
            user_id=user_id,
            conversation_id=conversation_id,
            error=str(e),
            request_id=request_id,
        )
        return None


async def _store_user_message(
    db, user_id: str, conversation_id: int, message: str, request_id: str
) -> bool:
    """
    Store user message to database

    Parameters:
        db: Database session
        user_id (str): User ID
        conversation_id (int): Conversation ID
        message (str): Message content
        request_id (str): Request ID for logging

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        MessageRepository.create(
            db=db,
            user_id=user_id,
            conversation_id=conversation_id,
            role="user",
            content=message,
        )
        logger.info(
            "user_message_stored",
            user_id=user_id,
            conversation_id=conversation_id,
            message_length=len(message),
            request_id=request_id,
        )
        return True

    except Exception as e:
        logger.error(
            "user_message_storage_failed",
            user_id=user_id,
            conversation_id=conversation_id,
            error=str(e),
            request_id=request_id,
        )
        return False


async def _execute_agent(
    user_id: str, conversation_id: int, user_message: str, request_id: str
) -> Dict[str, Any]:
    """
    Execute agent with conversation history and user message

    Parameters:
        user_id (str): User ID
        conversation_id (int): Conversation ID
        user_message (str): User's message
        request_id (str): Request ID for logging

    Returns:
        Dict with response text, tool_calls, and error status
    """
    try:
        # Build conversation context from database
        context = AgentContextBuilder.build_context(
            user_id=user_id,
            conversation_id=conversation_id,
        )

        if context["status"] != "success":
            logger.error(
                "context_building_failed",
                user_id=user_id,
                conversation_id=conversation_id,
                error=context.get("message", "Unknown error"),
                request_id=request_id,
            )
            return {
                "response": "Failed to build conversation context",
                "tool_calls": [],
                "error": "context_building_failed",
            }

        # Initialize and run agent
        agent_runner = AgentRunner()
        agent_initialized = await agent_runner.initialize_agent()
        if not agent_initialized:
            logger.error(
                "agent_initialization_failed",
                user_id=user_id,
                conversation_id=conversation_id,
                request_id=request_id,
            )
            return {
                "response": "Failed to initialize agent",
                "tool_calls": [],
                "error": "agent_initialization_failed",
            }

        # Execute agent with timeout
        try:
            agent_response = await asyncio.wait_for(
                agent_runner.run(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    user_message=user_message,
                    conversation_history=context["conversation_history"],
                ),
                timeout=AgentConfig.TIMEOUT_SECONDS,
            )

            if agent_response.error:
                logger.warning(
                    "agent_returned_error",
                    user_id=user_id,
                    conversation_id=conversation_id,
                    error=agent_response.error,
                    request_id=request_id,
                )
                return {
                    "response": agent_response.response,
                    "tool_calls": agent_response.tool_calls,
                    "error": agent_response.error,
                }

            logger.info(
                "agent_execution_successful",
                user_id=user_id,
                conversation_id=conversation_id,
                tool_calls_count=len(agent_response.tool_calls),
                response_length=len(agent_response.response),
                request_id=request_id,
            )

            return {
                "response": agent_response.response,
                "tool_calls": agent_response.tool_calls,
                "error": None,
            }

        except asyncio.TimeoutError:
            logger.error(
                "agent_execution_timeout",
                user_id=user_id,
                conversation_id=conversation_id,
                timeout_seconds=AgentConfig.TIMEOUT_SECONDS,
                request_id=request_id,
            )
            return {
                "response": "I'm taking too long to think. Please try again.",
                "tool_calls": [],
                "error": "timeout",
            }

    except Exception as e:
        logger.error(
            "agent_execution_exception",
            user_id=user_id,
            conversation_id=conversation_id,
            error=str(e),
            error_type=type(e).__name__,
            request_id=request_id,
        )
        return {
            "response": "An unexpected error occurred. Please try again.",
            "tool_calls": [],
            "error": "unexpected_error",
        }


async def _store_assistant_response(
    db,
    user_id: str,
    conversation_id: int,
    response_text: str,
    tool_calls: List[Dict[str, Any]],
    request_id: str,
) -> bool:
    """
    Store assistant response to database

    Parameters:
        db: Database session
        user_id (str): User ID
        conversation_id (int): Conversation ID
        response_text (str): Response text from agent
        tool_calls (List[Dict]): Tools invoked
        request_id (str): Request ID for logging

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        MessageRepository.create(
            db=db,
            user_id=user_id,
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
        )

        logger.info(
            "assistant_response_stored",
            user_id=user_id,
            conversation_id=conversation_id,
            response_length=len(response_text),
            tool_calls_count=len(tool_calls),
            request_id=request_id,
        )
        return True

    except Exception as e:
        logger.error(
            "assistant_response_storage_failed",
            user_id=user_id,
            conversation_id=conversation_id,
            error=str(e),
            request_id=request_id,
        )
        return False


async def _format_response(
    conversation_id: int,
    response_text: str,
    tool_calls: List[Dict[str, Any]],
) -> ChatResponse:
    """
    Format response into ChatResponse schema

    Parameters:
        conversation_id (int): Conversation ID
        response_text (str): Response text
        tool_calls (List[Dict]): Tools invoked

    Returns:
        ChatResponse: Formatted response
    """
    # Convert tool_calls to ToolCall models
    formatted_tool_calls = []
    for tool_call in tool_calls:
        try:
            formatted_tool_calls.append(
                ToolCall(
                    tool=tool_call.get("tool", "unknown"),
                    params=tool_call.get("params", {}),
                )
            )
        except Exception as e:
            logger.warning(
                "tool_call_formatting_failed",
                tool_call=tool_call,
                error=str(e),
            )

    return ChatResponse(
        conversation_id=conversation_id,
        response=response_text,
        tool_calls=formatted_tool_calls,
    )


# Export router
__all__ = ["router"]
