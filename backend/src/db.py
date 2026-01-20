"""
SQLAlchemy engine and session configuration for Neon PostgreSQL
Includes connection pooling with overflow protection (max_overflow=0)
"""

import os
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from .logging_config import get_logger

logger = get_logger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv(
    "NEON_DATABASE_URL", "postgresql://user:password@localhost/todo_chatbot"
)

# Create SQLAlchemy engine with connection pooling
# max_overflow=0: don't create additional connections beyond pool_size
# pool_size=20: maintain up to 20 connections in the pool
# echo=False: don't log SQL statements
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,  # Test connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session
    Usage: def route(db: Session = Depends(get_db_session)):
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_db_session_async() -> Generator[Session, None, None]:
    """
    Async dependency for FastAPI async routes
    Usage: async def route(db: Session = Depends(get_db_session_async)):
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_database_connection() -> bool:
    """
    Test database connection
    Returns: True if connection successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        return False


def get_connection_pool_status() -> dict:
    """
    Get connection pool statistics
    Returns: dict with pool size, checked-out connections, etc.
    """
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_out": pool.checkedout(),
        "pool_type": type(pool).__name__,
    }
