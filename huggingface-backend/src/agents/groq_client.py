"""
Groq Client Module
Provides streaming chat completions using Groq API with reasoning capabilities
Uses the openai/gpt-oss-120b model with extended thinking for complex reasoning
"""

import os
from typing import Any, AsyncGenerator, Dict, List, Optional

from groq import Groq

from ..logging_config import get_logger

logger = get_logger(__name__)


class GroqClient:
    """
    Groq Client for streaming chat completions
    Configured for openai/gpt-oss-120b model with reasoning capabilities
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "openai/gpt-oss-120b",
        temperature: float = 1.0,
        max_tokens: int = 8192,
        top_p: float = 1.0,
        reasoning_effort: str = "medium",
    ):
        """
        Initialize Groq client

        Parameters:
            api_key (str): Groq API key (defaults to GROQ_API_KEY env var)
            model (str): Model identifier (default: openai/gpt-oss-120b)
            temperature (float): Temperature for generation (0.0-1.0, default: 1.0)
            max_tokens (int): Maximum tokens in response (default: 8192)
            top_p (float): Top-p sampling parameter (default: 1.0)
            reasoning_effort (str): Reasoning effort level (default: "medium")
                - "low", "medium", "high"
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not provided and GROQ_API_KEY environment variable not set"
            )

        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.reasoning_effort = reasoning_effort

        logger.info(
            "groq_client_initialized",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        reasoning_effort: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completions from Groq API

        Parameters:
            messages (List[Dict]): List of message objects with 'role' and 'content'
            system_prompt (str, optional): System prompt to prepend
            temperature (float, optional): Override default temperature
            max_tokens (int, optional): Override default max tokens
            top_p (float, optional): Override default top_p
            reasoning_effort (str, optional): Override default reasoning effort

        Yields:
            str: Streamed text chunks from the model

        Example:
            ```python
            async for chunk in client.chat_stream(
                messages=[{"role": "user", "content": "Add a task to buy milk"}]
            ):
                print(chunk, end="", flush=True)
            ```
        """
        try:
            # Build messages with system prompt if provided
            request_messages = []
            if system_prompt:
                request_messages.append({"role": "system", "content": system_prompt})

            request_messages.extend(messages)

            logger.info(
                "groq_chat_stream_starting",
                model=self.model,
                message_count=len(request_messages),
                reasoning_effort=reasoning_effort or self.reasoning_effort,
            )

            # Create streaming completion
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=request_messages,
                temperature=temperature
                if temperature is not None
                else self.temperature,
                max_completion_tokens=max_tokens
                if max_tokens is not None
                else self.max_tokens,
                top_p=top_p if top_p is not None else self.top_p,
                reasoning_effort=reasoning_effort or self.reasoning_effort,
                stream=True,
                stop=None,
            )

            # Stream content chunks
            full_response = ""
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content

            logger.info(
                "groq_chat_stream_completed",
                model=self.model,
                response_length=len(full_response),
            )

        except Exception as e:
            logger.error(
                "groq_chat_stream_failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    async def chat_complete(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        reasoning_effort: Optional[str] = None,
    ) -> str:
        """
        Get non-streaming chat completion from Groq API

        Parameters:
            messages (List[Dict]): List of message objects
            system_prompt (str, optional): System prompt
            temperature (float, optional): Override temperature
            max_tokens (int, optional): Override max tokens
            top_p (float, optional): Override top_p
            reasoning_effort (str, optional): Override reasoning effort

        Returns:
            str: Complete response text

        Example:
            ```python
            response = await client.chat_complete(
                messages=[{"role": "user", "content": "What tasks do I have?"}],
                system_prompt="You are a task management assistant."
            )
            ```
        """
        try:
            # Build messages with system prompt if provided
            request_messages = []
            if system_prompt:
                request_messages.append({"role": "system", "content": system_prompt})

            request_messages.extend(messages)

            logger.info(
                "groq_chat_complete_starting",
                model=self.model,
                message_count=len(request_messages),
            )

            # Create non-streaming completion
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=request_messages,
                temperature=temperature
                if temperature is not None
                else self.temperature,
                max_completion_tokens=max_tokens
                if max_tokens is not None
                else self.max_tokens,
                top_p=top_p if top_p is not None else self.top_p,
                reasoning_effort=reasoning_effort or self.reasoning_effort,
                stream=False,
                stop=None,
            )

            # Extract response
            if completion.choices and completion.choices[0].message.content:
                response_text = completion.choices[0].message.content
                logger.info(
                    "groq_chat_complete_succeeded",
                    model=self.model,
                    response_length=len(response_text),
                )
                return response_text
            else:
                logger.warning("groq_chat_complete_empty_response")
                return ""

        except Exception as e:
            logger.error(
                "groq_chat_complete_failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    async def extract_tool_calls(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        tool_schema: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract tool calls from model response using structured prompting

        Parameters:
            messages (List[Dict]): Conversation messages
            system_prompt (str, optional): System prompt
            tool_schema (str, optional): Schema for tool calls as JSON format specification

        Returns:
            Dict with:
                - tools_identified: List of tool objects with name, params
                - reasoning: Model's reasoning
                - response: Natural language response

        Note:
            Since Groq doesn't support native function calling like OpenAI,
            we use prompt engineering to extract tool calls from the response.
        """
        try:
            # Build prompt for tool extraction
            tool_extraction_system = (
                (system_prompt or "")
                + """

IMPORTANT: After providing your response, ALWAYS include a JSON block at the end in this format:

<TOOL_CALLS>
{
  "tools": [
    {"name": "tool_name", "params": {"param1": "value1", "param2": "value2"}}
  ]
}
</TOOL_CALLS>

Only include tools that are actually needed for the user's request."""
            )

            if tool_schema:
                tool_extraction_system += f"\n\nAvailable tools schema:\n{tool_schema}"

            # Get response with streaming to collect full text
            full_response = ""
            async for chunk in self.chat_stream(
                messages=messages,
                system_prompt=tool_extraction_system,
                temperature=0.3,  # Lower temperature for structured extraction
            ):
                full_response += chunk

            # Parse tool calls from response
            tool_calls = self._parse_tool_calls_from_response(full_response)

            logger.info(
                "tool_calls_extracted",
                tools_found=len(tool_calls.get("tools", [])),
            )

            return {
                "tools_identified": tool_calls.get("tools", []),
                "response": self._extract_response_text(full_response),
                "full_response": full_response,
            }

        except Exception as e:
            logger.error(
                "tool_extraction_failed",
                error=str(e),
            )
            raise

    @staticmethod
    def _parse_tool_calls_from_response(response: str) -> Dict[str, Any]:
        """
        Parse tool calls from response text using JSON extraction

        Parameters:
            response (str): Full model response

        Returns:
            Dict with tools list
        """
        import json
        import re

        try:
            # Look for <TOOL_CALLS>...</TOOL_CALLS> markers (case-insensitive)
            if "<TOOL_CALLS>" in response or "<tool_calls>" in response:
                # Find markers (handle both cases)
                start_marker = response.find("<TOOL_CALLS>")
                end_marker = response.find("</TOOL_CALLS>")

                if start_marker == -1:
                    start_marker = response.find("<tool_calls>")
                    end_marker = response.find("</tool_calls>")

                if start_marker >= 0 and end_marker >= 0:
                    start = start_marker + (len("<TOOL_CALLS>") if "<TOOL_CALLS>" in response else len("<tool_calls>"))
                    json_str = response[start:end_marker].strip()

                    # Try to parse JSON
                    if json_str:
                        tool_calls_data = json.loads(json_str)
                        logger.info(
                            "tool_calls_extracted",
                            tools_found=len(tool_calls_data.get("tools", []))
                        )
                        return tool_calls_data

            logger.debug("no_tool_calls_in_response",
                        has_tool_markers="<TOOL_CALLS>" in response or "<tool_calls>" in response)
            return {"tools": []}

        except (json.JSONDecodeError, ValueError, AttributeError) as e:
            logger.warning("Failed to parse tool calls from response", error=str(e))
            return {"tools": []}

    @staticmethod
    def _extract_response_text(response: str) -> str:
        """
        Extract natural language response, removing tool calls markers

        Parameters:
            response (str): Full model response

        Returns:
            str: Response text without tool calls
        """
        # Handle both uppercase and lowercase tool call markers
        start_upper = response.find("<TOOL_CALLS>")
        start_lower = response.find("<tool_calls>")

        # Find the earliest marker (if any)
        start = -1
        if start_upper >= 0 and start_lower >= 0:
            start = min(start_upper, start_lower)
        elif start_upper >= 0:
            start = start_upper
        elif start_lower >= 0:
            start = start_lower

        if start >= 0:
            return response[:start].strip()
        return response


__all__ = ["GroqClient"]
