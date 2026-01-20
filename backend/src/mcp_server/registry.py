"""
MCP Tool Registry
Registers all tools with the MCP server and defines their schemas
"""

from typing import Any, Callable, Dict

from mcp.server import Server
from mcp.types import TextContent, Tool

from ..logging_config import get_logger
from .tools import (
    add_task,
    complete_task,
    delete_task,
    list_tasks,
    update_task,
)

logger = get_logger(__name__)


# Tool registry: maps tool names to their implementations
TOOL_REGISTRY: Dict[str, Callable] = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
    "delete_task": delete_task,
    "update_task": update_task,
}


def get_tool_schemas() -> Dict[str, Tool]:
    """
    Define JSON schemas for all MCP tools
    Returns a dictionary mapping tool names to their schema definitions
    """
    return {
        "add_task": Tool(
            name="add_task",
            description="Create a new task for the user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID (required)",
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (required, max 1000 chars)",
                        "maxLength": 1000,
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description (optional, max 1000 chars)",
                        "maxLength": 1000,
                    },
                },
                "required": ["user_id", "title"],
            },
        ),
        "list_tasks": Tool(
            name="list_tasks",
            description="Retrieve tasks for a user, optionally filtered by status",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID (required)",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter by status (optional, default: 'all')",
                        "default": "all",
                    },
                },
                "required": ["user_id"],
            },
        ),
        "complete_task": Tool(
            name="complete_task",
            description="Mark a task as completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID (required)",
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The task ID to complete (required)",
                        "minimum": 1,
                    },
                },
                "required": ["user_id", "task_id"],
            },
        ),
        "delete_task": Tool(
            name="delete_task",
            description="Delete a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID (required)",
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The task ID to delete (required)",
                        "minimum": 1,
                    },
                },
                "required": ["user_id", "task_id"],
            },
        ),
        "update_task": Tool(
            name="update_task",
            description="Update a task's title or description",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID (required)",
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The task ID to update (required)",
                        "minimum": 1,
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title (optional, max 1000 chars)",
                        "maxLength": 1000,
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description (optional, max 1000 chars)",
                        "maxLength": 1000,
                    },
                },
                "required": ["user_id", "task_id"],
            },
        ),
    }


def setup_tools(server: Server) -> None:
    """
    Register all MCP tools with the server

    Parameters:
        server (Server): The MCP Server instance
    """
    try:
        tool_schemas = get_tool_schemas()

        # Register each tool with the server
        for tool_name, tool_schema in tool_schemas.items():
            server.add_tool(tool_schema)
            logger.info("tool_registered", tool_name=tool_name)

        logger.info("all_tools_registered", count=len(tool_schemas))

    except Exception as e:
        logger.error("tool_registration_failed", error=str(e))
        raise


def call_tool(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call a registered MCP tool with the given input

    Parameters:
        tool_name (str): Name of the tool to call
        tool_input (dict): Input parameters for the tool

    Returns:
        dict: Tool result
    """
    if tool_name not in TOOL_REGISTRY:
        logger.warning("tool_not_found", tool_name=tool_name)
        return {"error": "tool_not_found", "message": f"Tool '{tool_name}' not found"}

    try:
        tool_func = TOOL_REGISTRY[tool_name]
        result = tool_func(**tool_input)
        logger.info("tool_executed", tool_name=tool_name, success="error" not in result)
        return result

    except Exception as e:
        logger.error("tool_execution_failed", tool_name=tool_name, error=str(e))
        return {
            "error": "tool_execution_failed",
            "message": f"Failed to execute tool '{tool_name}'",
        }


__all__ = ["setup_tools", "call_tool", "TOOL_REGISTRY", "get_tool_schemas"]
