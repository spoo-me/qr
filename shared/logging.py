"""
Logging utilities.

Provides:
- get_logger(): Get a configured logger instance
- hash_ip(): Hash IP addresses for privacy
- setup_logging(): Initialize the logging system
"""

import hashlib
import logging
import os
import sys
from typing import Optional

import structlog
from structlog.stdlib import BoundLogger
from structlog.types import EventDict, Processor

# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------
ENV = os.getenv("ENV", "development")
IS_PRODUCTION = ENV == "production"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if IS_PRODUCTION else "DEBUG")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json" if IS_PRODUCTION else "console")

# Sensitive fields to redact from logs
REDACTED_FIELDS = {
    "password",
    "token",
    "api_key",
    "authorization",
    "cookie",
    "secret",
    "key",
}


# ---------------------------------------------------------------------------
# IP hashing
# ---------------------------------------------------------------------------
def hash_ip(ip_address: Optional[str]) -> Optional[str]:
    """Hash IP address for privacy in production."""
    if ip_address is None:
        return None
    if IS_PRODUCTION and ip_address:
        return hashlib.sha256(ip_address.encode()).hexdigest()[:16]
    return ip_address


# ---------------------------------------------------------------------------
# Logger factory
# ---------------------------------------------------------------------------
def get_logger(name: str) -> BoundLogger:
    """Get a configured structlog logger instance."""
    return structlog.get_logger(name)


# ---------------------------------------------------------------------------
# structlog processors
# ---------------------------------------------------------------------------
def add_timestamp(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add ISO format timestamp to event dict."""
    from datetime import datetime, timezone

    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
    return event_dict


def redact_sensitive_fields(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Redact sensitive fields from logs."""
    for key in list(event_dict.keys()):
        if key.lower() in REDACTED_FIELDS or any(
            sensitive in key.lower()
            for sensitive in ["password", "token", "key", "secret"]
        ):
            if key not in ["level", "event", "timestamp", "logger"]:
                event_dict[key] = "***REDACTED***"
    return event_dict


def filter_exceptions(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Format exceptions properly for logging."""
    exc_info = event_dict.pop("exc_info", None)
    if exc_info:
        event_dict["exception"] = structlog.processors.format_exc_info(
            logger, method_name, {"exc_info": exc_info}
        )["exception"]
    return event_dict


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
def configure_structlog() -> None:
    """Configure structlog with appropriate processors for the environment."""
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        redact_sensitive_fields,
        filter_exceptions,
    ]

    if LOG_FORMAT == "json":
        structlog.configure(
            processors=shared_processors
            + [
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        _level_styles = structlog.dev.ConsoleRenderer.get_default_level_styles()
        _level_styles["debug"] = "\x1b[36m"
        structlog.configure(
            processors=shared_processors
            + [
                structlog.processors.format_exc_info,
                structlog.dev.ConsoleRenderer(
                    colors=True,
                    pad_event=15,
                    sort_keys=False,
                    level_styles=_level_styles,
                ),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )


def configure_stdlib_logging() -> None:
    """Configure standard library logging to work with structlog."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, LOG_LEVEL.upper()),
    )

    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("python_multipart").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)


def setup_logging() -> None:
    """Initialize logging system for the application."""
    configure_stdlib_logging()
    configure_structlog()

    logger = structlog.get_logger(__name__)
    logger.info(
        "logging_initialized",
        env=ENV,
        log_level=LOG_LEVEL,
        log_format=LOG_FORMAT,
    )
