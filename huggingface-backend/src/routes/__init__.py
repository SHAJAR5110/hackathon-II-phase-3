"""
Routes Package
Phase II - Todo Full-Stack Web Application

Contains all API route handlers organized by resource.
"""

from .chat import router as chat_router
from .tasks import router as tasks_router
from .users import router as users_router

__all__ = ["chat_router", "tasks_router", "users_router"]
