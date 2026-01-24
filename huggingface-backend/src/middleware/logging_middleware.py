"""
Request/response logging middleware for FastAPI
- Generates unique request_id for traceability
- Logs request: method, path, user_id, timestamp
- Logs response: status_code, latency_ms
- Uses structlog for JSON output
"""

import time
import uuid

from fastapi import Request

from ..logging_config import get_logger

logger = get_logger(__name__)


async def logging_middleware(request: Request, call_next):
    """
    Middleware to log request/response with timing and traceability
    - Generates unique request_id
    - Logs request details
    - Measures latency
    - Logs response details
    """
    # Generate unique request ID for traceability
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Get user_id if already authenticated
    user_id = getattr(request.state, "user_id", "anonymous")

    # Record start time
    start_time = time.time()

    # Log incoming request
    logger.info(
        "Incoming request",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        user_id=user_id,
        query=str(request.url.query)[:200] if request.url.query else None,
    )

    # Process request and get response
    try:
        response = await call_next(request)
    except Exception as exc:
        # Log exception and re-raise (will be caught by error middleware)
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error(
            "Request failed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            user_id=user_id,
            latency_ms=latency_ms,
            error_type=type(exc).__name__,
        )
        raise

    # Calculate latency
    latency_ms = int((time.time() - start_time) * 1000)

    # Log outgoing response
    logger.info(
        "Outgoing response",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        user_id=user_id,
        status_code=response.status_code,
        latency_ms=latency_ms,
    )

    # Add request_id to response headers for traceability
    response.headers["X-Request-ID"] = request_id

    return response


def generate_request_id() -> str:
    """Generate a unique request ID for traceability"""
    return str(uuid.uuid4())


__all__ = ["logging_middleware", "generate_request_id"]
