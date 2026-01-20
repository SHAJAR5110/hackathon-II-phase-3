"""
Database Configuration and Session Management
Phase II - Todo Full-Stack Web Application

Manages Neon PostgreSQL connection, async session factory, and database initialization.
"""

from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please configure it in the .env file with your Neon PostgreSQL connection string."
    )

# Convert postgresql:// to postgresql+asyncpg:// for async support
# Handle Neon and other PostgreSQL databases
if DATABASE_URL.startswith("postgresql://"):
    # Remove any query parameters (like ?sslmode=require) for asyncpg
    # asyncpg handles SSL differently than psycopg2
    base_url = DATABASE_URL.split("?")[0]  # Remove query params
    DATABASE_URL = base_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # Add SSL mode for asyncpg
    if "?" not in DATABASE_URL:
        DATABASE_URL += "?ssl=require"
elif DATABASE_URL.startswith("sqlite"):
    # Allow SQLite for testing
    pass
elif not DATABASE_URL.startswith("postgresql+asyncpg://"):
    raise ValueError(
        "DATABASE_URL must use PostgreSQL. "
        "Expected format: postgresql://user:password@host/database or sqlite://... for testing"
    )

# Create async engine
# echo=True enables SQL query logging (disable in production)
# SQLite doesn't support connection pooling, so we use NullPool
if DATABASE_URL.startswith("sqlite"):
    engine: AsyncEngine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Disable SQL logging for tests
        future=True,
        connect_args={"check_same_thread": False},  # SQLite specific
        poolclass=NullPool  # SQLite doesn't use connection pools
    )
else:
    # PostgreSQL (including Neon)
    engine: AsyncEngine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Disable SQL logging for cleaner output
        future=True,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=5,  # Connection pool size
        max_overflow=10,  # Max overflow connections
        connect_args={
            "server_settings": {"application_name": "todo_app"},
            "timeout": 30,
        },
    )

# Create async session maker
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Allow access to objects after commit
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that provides an async database session.

    Yields:
        AsyncSession: Database session for executing queries

    Usage:
        @router.get("/tasks")
        async def get_tasks(session: AsyncSession = Depends(get_session)):
            # Use session here
            pass

    The session is automatically committed and closed after the request.
    If an exception occurs, the session is rolled back.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in SQLModel models if they don't already exist.
    This function should be called on application startup.

    Note: For production, use proper migration tools like Alembic instead of
    creating tables directly. This is for MVP development only.
    """
    from models import User, Task  # Import models to register them

    # Log database type
    if DATABASE_URL.startswith("postgresql+asyncpg://"):
        db_type = "Neon PostgreSQL"
        # Hide password in logs
        display_url = DATABASE_URL.split("://")[1].split("@")[1]
        print(f"[DB] Connecting to {db_type} ({display_url})")
    elif DATABASE_URL.startswith("sqlite"):
        print("[DB] Using SQLite (in-memory)")
    else:
        print(f"[DB] Connecting to {DATABASE_URL}")

    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(SQLModel.metadata.create_all)
        print("[DB] Database tables initialized successfully")
    except Exception as e:
        print(f"[DB] Error initializing database: {str(e)}")
        raise


async def close_db() -> None:
    """
    Close database connections.

    Disposes of the engine and all connections in the pool.
    This function should be called on application shutdown.
    """
    await engine.dispose()
    print("[DB] Database connections closed")


# Database health check
async def check_db_health() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        bool: True if database is accessible, False otherwise

    Usage:
        health = await check_db_health()
        if not health:
            # Handle database connection error
    """
    try:
        from sqlalchemy import text
        async with async_session_maker() as session:
            # Execute a simple query to verify connection
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"[DB] Database health check failed: {e}")
        return False
