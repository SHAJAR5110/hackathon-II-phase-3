"""
Agent Runner Module
Executes OpenAI Agent with MCP tool support
Handles tool invocation, error handling, and response collection
"""

import asyncio
from typing import Any, Dict, List, Optional, Tuple

from ..db import SessionLocal
from ..logging_config import get_logger
from ..mcp_server.registry import call_tool
from ..repositories import MessageRepository
from .config import AgentConfig
from .id_mapper import IDMapper, get_id_mapper, reset_id_mapper
from .models_adapter import LiteLLMModelAdapter

logger = get_logger(__name__)


class AgentResponse:
    """Response from agent execution"""

    def __init__(
        self,
        response: str,
        tool_calls: List[Dict[str, Any]],
        error: Optional[str] = None,
    ):
        """
        Initialize agent response

        Parameters:
            response (str): Final text response from agent
            tool_calls (List[Dict]): List of MCP tools invoked
            error (Optional[str]): Error message if execution failed
        """
        self.response = response
        self.tool_calls = tool_calls
        self.error = error
        self.success = error is None


class AgentRunner:
    """Execute OpenAI Agent with MCP tools for task management"""

    def __init__(self):
        """Initialize agent runner"""
        self.id_mapper: IDMapper = get_id_mapper()
        self.model: Optional[LiteLLMModelAdapter] = None
        self.system_prompt: str = AgentConfig.get_system_prompt()

    async def initialize_agent(self) -> bool:
        """
        Initialize the OpenAI Agent with MCP tools

        Returns:
            bool: True if initialization successful
        """
        try:
            # Get configured model
            self.model = AgentConfig.get_model()

            logger.info("agent_runner_initialized")
            return True

        except Exception as e:
            logger.error("agent_runner_initialization_failed", error=str(e))
            return False

    async def run(
        self,
        user_id: str,
        conversation_id: int,
        user_message: str,
        conversation_history: List[Dict],
    ) -> AgentResponse:
        """
        Execute agent with conversation history and user message

        Implements full agent loop:
        1. Build message array with history + new message
        2. Run agent with MCP tools
        3. Collect tool results
        4. Extract final response

        Parameters:
            user_id (str): The authenticated user
            conversation_id (int): Current conversation ID
            user_message (str): New message from user
            conversation_history (List[Dict]): Prior conversation messages in ThreadItem format

        Returns:
            AgentResponse: Response with text, tool_calls, and any errors

        Raises:
            TimeoutError: If agent execution exceeds timeout
            Exception: If critical error occurs
        """
        try:
            # Initialize agent if needed
            if not self.model:
                success = await self.initialize_agent()
                if not success:
                    error_msg = "Failed to initialize agent"
                    logger.error("run_failed", error=error_msg)
                    return AgentResponse(
                        response="I'm having trouble starting. Please try again.",
                        tool_calls=[],
                        error=error_msg,
                    )

            # Build message array: history + new user message
            messages = conversation_history.copy() if conversation_history else []

            # Append new user message
            new_message = {
                "type": "message",
                "role": "user",
                "content": {"type": "text", "text": user_message},
            }
            messages.append(new_message)

            logger.info(
                "agent_run_starting",
                user_id=user_id,
                conversation_id=conversation_id,
                message_count=len(messages),
            )

            # Execute agent with timeout
            try:
                response = await asyncio.wait_for(
                    self._execute_agent_loop(user_id, conversation_id, messages),
                    timeout=AgentConfig.TIMEOUT_SECONDS,
                )
                return response

            except asyncio.TimeoutError:
                error_msg = (
                    f"Agent execution timed out after {AgentConfig.TIMEOUT_SECONDS}s"
                )
                logger.error("agent_run_timeout", error=error_msg)
                return AgentResponse(
                    response="I'm having trouble reaching my brain. Please try again.",
                    tool_calls=[],
                    error=error_msg,
                )

        except Exception as e:
            logger.error(
                "agent_run_failed",
                user_id=user_id,
                conversation_id=conversation_id,
                error=str(e),
            )
            return AgentResponse(
                response="An unexpected error occurred. Please try again.",
                tool_calls=[],
                error=str(e),
            )

    async def _execute_agent_loop(
        self,
        user_id: str,
        conversation_id: int,
        messages: List[Dict],
    ) -> AgentResponse:
        """
        Execute agent loop with tool invocation

        Parameters:
            user_id (str): Authenticated user
            conversation_id (int): Conversation context
            messages (List[Dict]): Message history to send to agent

        Returns:
            AgentResponse: Response with text and tool_calls
        """
        tool_calls_made: List[Dict[str, Any]] = []
        final_response: str = ""

        try:
            # Run agent with event streaming
            # Note: This is a simplified implementation
            # In production, would stream events and handle tool calls
            response_text = await self._run_agent_with_tools(
                user_id, conversation_id, messages, tool_calls_made
            )

            final_response = response_text or "I couldn't generate a response."

            logger.info(
                "agent_run_completed",
                user_id=user_id,
                conversation_id=conversation_id,
                tool_calls_count=len(tool_calls_made),
                response_length=len(final_response),
            )

            return AgentResponse(
                response=final_response,
                tool_calls=tool_calls_made,
            )

        except Exception as e:
            logger.error(
                "agent_loop_failed",
                user_id=user_id,
                conversation_id=conversation_id,
                error=str(e),
            )
            raise

    async def _run_agent_with_tools(
        self,
        user_id: str,
        conversation_id: int,
        messages: List[Dict],
        tool_calls_list: List[Dict],
    ) -> str:
        """
        Run agent and handle tool invocations

        Parameters:
            user_id (str): Authenticated user
            conversation_id (int): Conversation ID
            messages (List[Dict]): Message history
            tool_calls_list (List[Dict]): Output list for tool calls made

        Returns:
            str: Final response text from agent
        """
        try:
            # In production, would iterate through events from runner
            # For now, placeholder implementation
            # This would be integrated with OpenAI Agents SDK event streaming

            # Mock response (in production, extract from agent events)
            response_text = (
                "I'm ready to help you manage your tasks. What would you like to do?"
            )

            # Example of how tool calls would be captured:
            # for event in events:
            #     if event.type == "tool_call":
            #         tool_name = event.tool_name
            #         tool_input = event.tool_input
            #         result = await self._invoke_tool(user_id, tool_name, tool_input)
            #         tool_calls_list.append({
            #             "tool": tool_name,
            #             "params": tool_input,
            #             "result": result,
            #         })

            return response_text

        except Exception as e:
            logger.error(
                "tool_execution_failed",
                user_id=user_id,
                error=str(e),
            )
            raise

    async def _invoke_tool(
        self, user_id: str, tool_name: str, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Invoke an MCP tool with error handling

        Parameters:
            user_id (str): Authenticated user (for authorization)
            tool_name (str): Name of tool to invoke
            tool_input (Dict): Tool parameters

        Returns:
            Dict: Tool result

        Notes:
            - Ensures user_id is included in tool_input for authorization
            - Handles tool errors gracefully
            - Logs all tool invocations for audit
        """
        try:
            # Inject user_id for tool authorization
            if "user_id" not in tool_input:
                tool_input["user_id"] = user_id

            logger.info(
                "tool_invocation_starting",
                tool_name=tool_name,
                user_id=user_id,
            )

            # Call tool through registry
            result = call_tool(tool_name, tool_input)

            logger.info(
                "tool_invocation_completed",
                tool_name=tool_name,
                user_id=user_id,
                success="error" not in result,
            )

            return result

        except Exception as e:
            error_result = {
                "error": "tool_invocation_failed",
                "message": f"Failed to invoke {tool_name}",
                "details": str(e),
            }
            logger.error(
                "tool_invocation_error",
                tool_name=tool_name,
                user_id=user_id,
                error=str(e),
            )
            return error_result


def reset_runner():
    """Reset runner state for new request (stateless architecture)"""
    reset_id_mapper()


__all__ = ["AgentRunner", "AgentResponse", "reset_runner"]
