"""Structured logging configuration using structlog.

This module sets up structured logging with proper formatting,
request ID tracking, and contextual information.
"""

import logging
import sys
import uuid
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Optional

import structlog
from structlog.types import EventDict, Processor

# Context variable for request ID tracking
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def add_request_id(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add request ID to log entries.

    Args:
        logger: The logger instance
        method_name: The name of the logging method
        event_dict: The event dictionary to process

    Returns:
        Modified event dictionary with request ID
    """
    request_id = request_id_ctx.get()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def add_log_level(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add log level to event dict.

    Args:
        logger: The logger instance
        method_name: The name of the logging method
        event_dict: The event dictionary to process

    Returns:
        Modified event dictionary with log level
    """
    if method_name == "warn":
        # Standardize to "warning"
        event_dict["level"] = "warning"
    else:
        event_dict["level"] = method_name
    return event_dict


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    json_logs: bool = False,
) -> None:
    """Configure structured logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files. If None, logs to console only
        json_logs: If True, output logs in JSON format
    """
    # Convert log level string to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Shared processors for all configurations
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        add_request_id,
        add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        # JSON output for production
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Human-readable output for development
        processors = shared_processors + [
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    # Set up file logging if log directory is specified
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setLevel(level)

        # Add formatter for file logs
        if json_logs:
            file_handler.setFormatter(
                logging.Formatter("%(message)s")
            )
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                )
            )

        # Add handler to root logger
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """Get a logger instance.

    Args:
        name: Logger name, typically __name__ of the calling module

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def set_request_id(request_id: Optional[str] = None) -> str:
    """Set the request ID for the current context.

    Args:
        request_id: Request ID to set. If None, generates a new UUID

    Returns:
        The request ID that was set
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_ctx.set(request_id)
    return request_id


def clear_request_id() -> None:
    """Clear the request ID from the current context."""
    request_id_ctx.set(None)


def get_request_id() -> Optional[str]:
    """Get the current request ID.

    Returns:
        Current request ID or None if not set
    """
    return request_id_ctx.get()


# Convenience function for logging with context
def log_with_context(
    logger: structlog.stdlib.BoundLogger,
    level: str,
    message: str,
    **kwargs: Any,
) -> None:
    """Log a message with additional context.

    Args:
        logger: The logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **kwargs: Additional context to include in the log
    """
    log_method = getattr(logger, level.lower())
    log_method(message, **kwargs)
