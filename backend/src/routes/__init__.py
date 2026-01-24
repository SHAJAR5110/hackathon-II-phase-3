"""
API Routes - All endpoints for the todo chatbot application
Feature: 1-chatbot-ai
"""

from .chat import router as chat_router
from .tasks import router as tasks_router

__all__ = ["chat_router", "tasks_router"]
