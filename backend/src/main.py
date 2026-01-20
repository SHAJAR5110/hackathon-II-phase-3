"""
FastAPI application for AI-Powered Todo Chatbot with MCP Integration
Feature: 1-chatbot-ai
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .logging_config import get_logger, setup_logging
from .middleware.auth import auth_middleware
from .middleware.errors import error_handling_middleware
from .middleware.logging_middleware import logging_middleware
from .routes import chat_router

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events"""
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register middleware in order (innermost first):
# 1. Error handling (catches all exceptions)
# 2. Authentication (validates user_id from header)
# 3. Request/response logging (with request_id traceability)
app.middleware("http")(error_handling_middleware)
app.middleware("http")(auth_middleware)
app.middleware("http")(logging_middleware)

# Include routers
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
