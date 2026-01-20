"""
Structured logging configuration using structlog
All logs output as JSON with context: user_id, conversation_id, tool_name, latency
"""

import os
import sys
import json
from datetime import datetime
import structlog
from structlog.processors import JSONRenderer, KeyValueRenderer


def setup_logging():
    """Configure structlog for structured JSON logging"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure Python logging to use structlog
    import logging

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level),
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a logger instance with optional context binding"""
    return structlog.get_logger(name or __name__)


# Example usage:
# logger = get_logger(__name__)
# logger.info("operation", user_id="user123", conversation_id=1, tool_name="add_task", latency_ms=245, status="success")
