"""Logging configuration module - structured logging with JSON formatter.

Provides JSON-based structured logging for production observability and
human-readable text logging for development.
"""

import logging
import json
import sys
from typing import Dict, Any


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging.

    Outputs logs in JSON format for machine parsing.

    Example output:
        {"timestamp": "2025-01-13T10:30:45", "level": "INFO",
         "message": "prp.execution.started", "prp_id": "PRP-003"}
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON string

        Note: Includes extra fields from record.extra dict if provided.
        """
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields from record
        if hasattr(record, "prp_id"):
            log_data["prp_id"] = record.prp_id
        if hasattr(record, "phase"):
            log_data["phase"] = record.phase
        if hasattr(record, "duration"):
            log_data["duration"] = record.duration
        if hasattr(record, "success"):
            log_data["success"] = record.success

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(
    level: str = "INFO",
    json_output: bool = False,
    log_file: str = None
) -> logging.Logger:
    """Setup application logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_output: If True, use JSON formatter
        log_file: Optional file path for file logging

    Returns:
        Configured root logger

    Example:
        setup_logging(level="DEBUG", json_output=True)
        logger = logging.getLogger(__name__)
        logger.info("prp.started", extra={"prp_id": "PRP-003"})

    Note: Call this once at application startup. All subsequent loggers
    will inherit this configuration.
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    if json_output:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter())  # Always use JSON for file logs
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger for module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance configured with application settings

    Example:
        logger = get_logger(__name__)
        logger.info("Starting operation", extra={"prp_id": "PRP-003"})

    Note: Use this instead of logging.getLogger() for consistency.
    """
    return logging.getLogger(name)
