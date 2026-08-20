"""
Logging configuration for SQLite Database Manager.

This module sets up logging for the application with file and console handlers.
"""

import logging
import sys
from pathlib import Path

from core.config import LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT, LOG_LEVEL_DEFAULT, ensure_directories


def setup_logger(
    name: str = "sqlite_manager",
    log_level: str = LOG_LEVEL_DEFAULT,
    log_file: Path | None = None,
) -> logging.Logger:
    """
    Set up and return a logger with file and console handlers.

    Args:
        name: Logger name (usually __name__ of the calling module).
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Path to log file. If None, uses default from config.

    Returns:
        Configured logger instance.
    """
    # Ensure directories exist
    ensure_directories()

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_file is None:
        log_file = LOG_FILE

    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Log all levels to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (OSError, PermissionError) as e:
        # If we can't create log file, just use console
        logger.warning(f"Could not create log file at {log_file}: {e}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one.

    Args:
        name: Logger name (usually __name__ of the calling module).

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)


# Create default logger for the application
default_logger = setup_logger()
