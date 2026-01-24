"""
Agent Runner Module
Executes Groq Agent with MCP tool support
Handles tool invocation, error handling, and response collection using Groq API
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple

from ..db import SessionLocal
from ..logging_config import get_logger
from ..mcp_server.registry import call_tool
from ..repositories import MessageRepository
from .config import AgentConfig
from .groq_client import GroqClient
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
    """Execute Groq Agent with MCP tools for task management"""

    def __init__(self):
        """Initialize agent runner"""
        self.id_mapper: IDMapper = get_id_mapper()
        self.groq_client: Optional[GroqClient] = None
        self.system_prompt: str = AgentConfig.get_system_prompt()
        self.tool_schema: str = AgentConfig.get_tool_schema()

    async def initialize_agent(self) -> bool:
        """
        Initialize the Groq Agent with MCP tools

        Returns:
            bool: True if initialization successful
        """
        try:
            # Initialize Groq client
            self.groq_client = GroqClient(
                model=AgentConfig.GROQ_MODEL,
                temperature=AgentConfig.TEMPERATURE,
                max_tokens=AgentConfig.MAX_TOKENS,
                top_p=AgentConfig.TOP_P,
                reasoning_effort=AgentConfig.REASONING_EFFORT,
            )

            logger.info(
                "agent_runner_initialized",
                model=AgentConfig.GROQ_MODEL,
            )
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
        2. Run agent with Groq API using reasoning
        3. Extract tool calls from response
        4. Invoke MCP tools
        5. Return final response

        Parameters:
            user_id (str): The authenticated user
            conversation_id (int): Current conversation ID
            user_message (str): New message from user
            conversation_history (List[Dict]): Prior conversation messages

        Returns:
            AgentResponse: Response with text, tool_calls, and any errors

        Raises:
            TimeoutError: If agent execution exceeds timeout
            Exception: If critical error occurs
        """
        try:
            # Initialize agent if needed
            if not self.groq_client:
                success = await self.initialize_agent()
                if not success:
                    error_msg = "Failed to initialize Groq agent"
                    logger.error("run_failed", error=error_msg)
                    return AgentResponse(
                        response="I'm having trouble starting. Please try again.",
                        tool_calls=[],
                        error=error_msg,
                    )

            # Convert ThreadItem format to standard message format if needed
            messages = self._convert_messages(conversation_history)

            # Append new user message
            messages.append(
                {
                    "role": "user",
                    "content": user_message,
                }
            )

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
                    response="I'm taking too long to think. Please try again.",
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

    def _convert_messages(self, conversation_history: List[Dict]) -> List[Dict]:
        """
        Convert ThreadItem format to standard message format

        Parameters:
            conversation_history (List[Dict]): Messages in ThreadItem format

        Returns:
            List[Dict]: Messages in standard format for Groq API
        """
        messages = []
        for item in conversation_history:
            if isinstance(item, dict):
                # ThreadItem format: {"type": "message", "role": "user", "content": {...}}
                if item.get("type") == "message" and "role" in item:
                    content = item.get("content")
                    # Extract text if content is a structured block
                    if isinstance(content, dict):
                        text = content.get("text", "")
                    else:
                        text = str(content)

                    messages.append(
                        {
                            "role": item["role"],
                            "content": text,
                        }
                    )
                # Standard format: {"role": "user", "content": "text"}
                elif "role" in item and "content" in item:
                    messages.append(item)

        return messages

    async def _execute_agent_loop(
        self,
        user_id: str,
        conversation_id: int,
        messages: List[Dict],
    ) -> AgentResponse:
        """
        Execute agent loop with tool invocation using Groq

        Parameters:
            user_id (str): Authenticated user
            conversation_id (int): Conversation context
            messages (List[Dict]): Message history to send to agent

        Returns:
            AgentResponse: Response with text and tool_calls
        """
        tool_calls_made: List[Dict[str, Any]] = []

        try:
            # Run agent with Groq and tool extraction
            response_data = await self._run_agent_with_tools(
                user_id, conversation_id, messages, tool_calls_made
            )

            final_response = response_data.get(
                "response", "I couldn't generate a response."
            )

            logger.info(
                "agent_loop_completed",
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
    ) -> Dict[str, Any]:
        """
        Run Groq agent and handle tool invocations

        Implementation:
        1. Send messages to Groq API with extended thinking
        2. Extract tool calls from response using structured prompting
        3. Invoke MCP tools based on identified needs
        4. Collect tool results and invoke agent again if needed
        5. Return final response with all tool calls made

        Parameters:
            user_id (str): Authenticated user
            conversation_id (int): Conversation ID
            messages (List[Dict]): Message history
            tool_calls_list (List[Dict]): Output list for tool calls made

        Returns:
            Dict with response text and any errors
        """
        try:
            logger.info(
                "agent_with_tools_executing",
                user_id=user_id,
                conversation_id=conversation_id,
                total_messages=len(messages),
                model=AgentConfig.GROQ_MODEL,
            )

            # Get response from Groq with tool extraction
            tool_extraction_result = await self.groq_client.extract_tool_calls(
                messages=messages,
                system_prompt=self.system_prompt,
                tool_schema=self.tool_schema,
            )

            response_text = tool_extraction_result.get("response", "")
            tools_identified = tool_extraction_result.get("tools_identified", [])

            # Invoke identified tools and collect results
            tool_results = []
            for tool_spec in tools_identified:
                try:
                    tool_name = tool_spec.get("name")
                    tool_params = tool_spec.get("params", {})

                    if not tool_name:
                        logger.warning("Tool spec missing name", tool_spec=tool_spec)
                        continue

                    # Invoke MCP tool
                    tool_result = await self._invoke_tool(
                        user_id, tool_name, tool_params
                    )

                    tool_results.append(
                        {
                            "tool": tool_name,
                            "params": tool_params,
                            "result": tool_result,
                            "success": "error" not in tool_result,
                        }
                    )

                    tool_calls_list.append(
                        {
                            "tool": tool_name,
                            "params": tool_params,
                        }
                    )

                    logger.info(
                        "tool_invoked_successfully",
                        user_id=user_id,
                        tool_name=tool_name,
                        success=not ("error" in tool_result),
                    )

                except Exception as e:
                    logger.error(
                        "tool_invocation_error",
                        user_id=user_id,
                        tool_name=tool_spec.get("name", "unknown"),
                        error=str(e),
                    )
                    tool_results.append(
                        {
                            "tool": tool_spec.get("name", "unknown"),
                            "error": str(e),
                            "success": False,
                        }
                    )

            # If tools were invoked, optionally get follow-up response from agent
            if tool_results:
                # Build follow-up message with tool results
                assistant_message = {
                    "role": "assistant",
                    "content": response_text,
                }
                tool_results_message = {
                    "role": "user",
                    "content": f"Tool execution results:\n{json.dumps(tool_results, indent=2)}",
                }

                follow_up_messages = messages + [
                    assistant_message,
                    tool_results_message,
                ]

                # Get follow-up response
                try:
                    follow_up_response = await self.groq_client.chat_complete(
                        messages=follow_up_messages,
                        system_prompt=self.system_prompt,
                    )
                    if follow_up_response:
                        response_text = follow_up_response
                except Exception as e:
                    logger.warning(
                        "follow_up_response_failed",
                        error=str(e),
                    )
                    # Continue with original response if follow-up fails

            logger.info(
                "agent_with_tools_completed",
                user_id=user_id,
                conversation_id=conversation_id,
                tool_calls_made=len(tool_calls_list),
                response_length=len(response_text),
            )

            return {
                "response": response_text,
                "tool_calls": tool_calls_list,
            }

        except Exception as e:
            logger.error(
                "agent_with_tools_failed",
                user_id=user_id,
                conversation_id=conversation_id,
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
