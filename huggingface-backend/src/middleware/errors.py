"""
Global error handling middleware for FastAPI
- Catches all exceptions globally
- Logs with context: user_id, endpoint, method, exception type
- Returns structured error responses with request_id
- Maps database errors to user-friendly messages
- Never exposes stack traces to client
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError

from ..logging_config import get_logger

logger = get_logger(__name__)


async def error_handling_middleware(request: Request, call_next):
    """
    Global error handling middleware
    Catches and logs all exceptions, returns structured error responses
    HTTPException is re-raised to allow FastAPI's built-in handlers to process it
    """
    try:
        response = await call_next(request)
        return response

    except HTTPException:
        # Re-raise HTTPException so FastAPI can handle it natively
        raise

    except Exception as exc:
        # Get context from request state
        user_id = getattr(request.state, "user_id", "anonymous")
        request_id = getattr(request.state, "request_id", "unknown")
        exc_type = type(exc).__name__

        # Log the exception with full context
        logger.error(
            "Unhandled exception",
            user_id=user_id,
            path=request.url.path,
            method=request.method,
            exception_type=exc_type,
            exception_message=str(exc)[:200],  # Truncate for logging
            request_id=request_id,
        )

        # Handle database-specific errors
        if isinstance(exc, IntegrityError):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Invalid data provided",
                    "message": "The data you provided violates database constraints",
                    "request_id": request_id,
                },
            )

        if isinstance(exc, OperationalError):
            logger.critical(
                "Database connection error",
                user_id=user_id,
                request_id=request_id,
            )
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service temporarily unavailable",
                    "message": "Database connection failed. Please try again later.",
                    "request_id": request_id,
                },
            )

        # Generic error response (no stack trace exposed)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred. Our team has been notified.",
                "request_id": request_id,
            },
        )


def format_error_response(
    status_code: int,
    error: str,
    message: str = None,
    request_id: str = "unknown",
) -> dict:
    """
    Format standardized error response

    Args:
        status_code: HTTP status code
        error: Error type/code
        message: Human-readable message
        request_id: Request ID for tracing

    Returns:
        Structured error dict
    """
    response = {
        "error": error,
        "request_id": request_id,
    }
    if message:
        response["message"] = message
    return response


__all__ = ["error_handling_middleware", "format_error_response"]
