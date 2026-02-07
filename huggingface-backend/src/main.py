"""
FastAPI application for AI-Powered Todo Chatbot with MCP Integration
Feature: 1-chatbot-ai
"""

# Load environment variables FIRST - before any other imports
import os
from pathlib import Path

# Load .env from the backend directory
env_path = Path(__file__).parent.parent / ".env"
from dotenv import load_dotenv
load_dotenv(dotenv_path=env_path, override=True)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .logging_config import get_logger, setup_logging
# from .middleware.auth import auth_middleware  # Not needed - auth is handled per-route
from .middleware.errors import error_handling_middleware
from .middleware.logging_middleware import logging_middleware
from .routes import chat_router, tasks_router, users_router
from .routes.auth import router as auth_router

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events
    
    NOTE: MCP Server Integration (Phase 7)
    The MCP server for tool management is currently initialized in registry.py
    but not actively used in the agent pipeline yet. Full OpenAI Agents SDK
    integration with MCP tools will be implemented in Phase 7 (Frontend Integration).
    
    When ready to implement:
    1. Import MCP server: from .mcp_server import start_server
    2. Start in lifespan: server = start_server()
    3. Register tools and ensure proper lifecycle management
    """
    # Initialize database on startup
    from .db import init_db
    await init_db()
    
    logger.info(
        "Application starting up", environment=os.getenv("ENVIRONMENT", "development")
    )
    yield
    logger.info("Application shutting down")


# Create FastAPI application
app = FastAPI(
    title="AI-Powered Todo Chatbot",
    description="Conversational task management with MCP tools",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
# Allow requests from frontend during development
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register middleware in order (LIFO - registered last executes first):
# Note: FastAPI middleware stack is LIFO, so innermost (first to execute) is registered last
# Execution order: logging_middleware → error_handling_middleware
# 1. logging_middleware: Generate request_id and log incoming requests
# 2. error_handling_middleware: Catch all exceptions and format responses
# Auth is handled per-route using Depends(get_current_user_id)
app.middleware("http")(error_handling_middleware)
app.middleware("http")(logging_middleware)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(chat_router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "AI-Powered Todo Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "chat": "/api/{user_id}/chat",
        },
    }


# Note: Global exception handling is done via middleware (error_handling_middleware)
# to ensure proper context (user_id, request_id) is available in logs


# Startup message
if __name__ == "__main__":
    logger.info("Starting FastAPI server")
    import uvicorn

    uvicorn.run(
        "backend.src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "false").lower() == "true",
    )
