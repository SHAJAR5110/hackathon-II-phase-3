"""
API Routes - All endpoints for the todo chatbot application
Feature: 1-chatbot-ai
"""

from .chat import router as chat_router

__all__ = ["chat_router"]
