"""
MCP Server Foundation - Official MCP SDK Integration
Initializes the Model Context Protocol server with task management tools
"""

from mcp.server import Server

from .registry import setup_tools

# Initialize MCP Server
server = Server(name="todo-mcp-server", version="1.0.0")


def start_server():
    """
    Start the MCP server and register all tools
    Called during application startup
    """
    try:
        # Register all MCP tools with the server
        setup_tools(server)
        return server
    except Exception as e:
        raise RuntimeError(f"Failed to start MCP server: {str(e)}")


__all__ = ["server", "start_server"]
