"""
Database utility functions
- Session context managers (sync and async)
- Health checks
- Connection pool status
"""

from contextlib import asynccontextmanager, contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from .db import (
    SessionLocal,
    engine,
    get_connection_pool_status,
    test_database_connection,
)
from .logging_config import get_logger

logger = get_logger(__name__)


@contextmanager
def get_db_session_context() -> Generator[Session, None, None]:
    """
    Context manager for database session (synchronous)
    Usage:
        with get_db_session_context() as db:
            task = TaskRepository.read(db, user_id, task_id)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def get_db_session_async_context() -> Generator[Session, None, None]:
    """
    Context manager for database session (asynchronous)
    Usage:
        async with get_db_session_async_context() as db:
            task = TaskRepository.read(db, user_id, task_id)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def health_check() -> dict:
    """
    Check database health
    Returns: {
        "status": "healthy" | "unhealthy",
        "database": True | False,
        "pool_status": {...}
    }
    """
    db_ok = test_database_connection()
    pool_status = get_connection_pool_status() if db_ok else {}

    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": db_ok,
        "pool_status": pool_status,
    }


def get_db_stats() -> dict:
    """
    Get database statistics
    Returns: Connection pool stats and database health
    """
    try:
        pool_status = get_connection_pool_status()
        db_ok = test_database_connection()

        return {
            "connection_ok": db_ok,
            "pool": pool_status,
        }
    except Exception as e:
        logger.error("Failed to get database stats", error=str(e))
        return {
            "connection_ok": False,
            "error": str(e),
        }


def init_db() -> bool:
    """
    Initialize database (test connection)
    Returns: True if successful, False otherwise
    """
    try:
        logger.info("Initializing database connection")
        if test_database_connection():
            logger.info("Database initialized successfully")
            return True
        else:
            logger.error("Database initialization failed")
            return False
    except Exception as e:
        logger.error("Database initialization error", error=str(e))
        return False
