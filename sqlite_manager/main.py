#!/usr/bin/env python3
"""
SQLite Database Manager - Main Entry Point

A desktop application for managing SQLite databases using PySide6.

Usage:
    python main.py [--log-level LEVEL]

Options:
    --log-level  Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
"""

import sys
import argparse

from core.config import LOG_LEVEL_DEFAULT, ensure_directories
from utils.logger import setup_logger


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="SQLite Database Manager - A visual database management tool"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=LOG_LEVEL_DEFAULT,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f"Set logging level (default: {LOG_LEVEL_DEFAULT})"
    )
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the application.

    Returns:
        Application exit code.
    """
    # Parse arguments
    args = parse_arguments()

    # Ensure directories exist
    ensure_directories()

    # Set up logging with specified level
    setup_logger("sqlite_manager", log_level=args.log_level)

    # Import and run application
    from app.application import main as app_main

    return app_main()


if __name__ == "__main__":
    sys.exit(main())
