"""
Application configuration constants.

This module contains all configuration values used throughout the application.
"""

from pathlib import Path
from typing import Final


# Application Info
APP_NAME: Final[str] = "SQLite Database Manager"
APP_VERSION: Final[str] = "1.0.0"
APP_AUTHOR: Final[str] = "SQLite Database Manager Team"

# Default window settings
DEFAULT_WINDOW_WIDTH: Final[int] = 1200
DEFAULT_WINDOW_HEIGHT: Final[int] = 800
MIN_WINDOW_WIDTH: Final[int] = 800
MIN_WINDOW_HEIGHT: Final[int] = 600

# Sidebar settings
SIDEBAR_DEFAULT_WIDTH: Final[int] = 250
SIDEBAR_MIN_WIDTH: Final[int] = 150
SIDEBAR_MAX_WIDTH: Final[int] = 500

# Database settings
DEFAULT_PAGE_SIZE: Final[int] = 100  # For pagination
SUPPORTED_EXTENSIONS: Final[tuple[str, ...]] = (".db", ".sqlite", ".sqlite3")
BACKUP_EXTENSION: Final[str] = ".backup"

# SQL settings
DEFAULT_LIMIT: Final[int] = 100  # Default LIMIT for queries
MAX_QUERY_HISTORY: Final[int] = 100  # Maximum number of queries to store in history

# Logging settings
LOG_LEVEL_DEFAULT: Final[str] = "INFO"
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

# Paths
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent
LOGS_DIR: Final[Path] = BASE_DIR / "logs"
CONFIG_DIR: Final[Path] = BASE_DIR / "config"
RESOURCES_DIR: Final[Path] = BASE_DIR / "resources"
STYLES_DIR: Final[Path] = BASE_DIR / "styles"

# File paths
LOG_FILE: Final[Path] = LOGS_DIR / "app.log"
SETTINGS_FILE: Final[Path] = CONFIG_DIR / "settings.json"
QUERY_HISTORY_FILE: Final[Path] = CONFIG_DIR / "query_history.json"

# Theme settings
THEME_LIGHT: Final[str] = "light"
THEME_DARK: Final[str] = "dark"
DEFAULT_THEME: Final[str] = THEME_LIGHT

# Icons (will be loaded from resources)
ICON_DATABASE: Final[str] = ":/icons/database.svg"
ICON_TABLE: Final[str] = ":/icons/table.svg"
ICON_VIEW: Final[str] = ":/icons/view.svg"
ICON_INDEX: Final[str] = ":/icons/index.svg"
ICON_TRIGGER: Final[str] = ":/icons/trigger.svg"

# Dialog settings
CONFIRM_DESTRUCTIVE_OPERATIONS: Final[bool] = True
MAX_PREVIEW_ROWS: Final[int] = 10  # For import preview


def ensure_directories() -> None:
    """Ensure all required directories exist."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
