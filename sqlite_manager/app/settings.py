"""
Application settings for SQLite Database Manager.

This module handles loading and saving application settings.
"""

import json
from pathlib import Path
from typing import Any

from core.config import SETTINGS_FILE, DEFAULT_THEME, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from utils.logger import get_logger


logger = get_logger(__name__)


class Settings:
    """
    Application settings manager.

    This class handles loading, saving, and accessing application settings.

    Attributes:
        theme: Current theme (light/dark).
        window_width: Window width.
        window_height: Window height.
        recent_files: List of recently opened database files.
        foreign_keys_enabled: Default foreign key setting.
    """

    def __init__(self) -> None:
        """Initialize settings with default values."""
        self._settings: dict[str, Any] = {
            "theme": DEFAULT_THEME,
            "window_width": DEFAULT_WINDOW_WIDTH,
            "window_height": DEFAULT_WINDOW_HEIGHT,
            "recent_files": [],
            "foreign_keys_enabled": True,
            "sidebar_width": 250,
            "last_opened_dir": str(Path.home()),
            "max_query_history": 100,
            "page_size": 100,
            "confirm_destructive_operations": True,
        }
        self._settings_file = SETTINGS_FILE
        self.load()

    def load(self) -> None:
        """Load settings from file."""
        if not self._settings_file.exists():
            logger.debug("Settings file not found, using defaults")
            return

        try:
            with open(self._settings_file, "r", encoding="utf-8") as f:
                loaded_settings = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            self._settings.update(loaded_settings)
            logger.info(f"Settings loaded from {self._settings_file}")

        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load settings: {e}, using defaults")

    def save(self) -> None:
        """Save settings to file."""
        try:
            # Ensure directory exists
            self._settings_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self._settings_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2)

            logger.info(f"Settings saved to {self._settings_file}")

        except OSError as e:
            logger.error(f"Failed to save settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key.
            default: Default value if key doesn't exist.

        Returns:
            Setting value or default.
        """
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value.

        Args:
            key: Setting key.
            value: Setting value.
        """
        self._settings[key] = value
        logger.debug(f"Setting updated: {key} = {value}")

    @property
    def theme(self) -> str:
        """Get current theme."""
        return self._settings.get("theme", DEFAULT_THEME)

    @theme.setter
    def theme(self, value: str) -> None:
        """Set theme."""
        self._settings["theme"] = value

    @property
    def window_width(self) -> int:
        """Get window width."""
        return self._settings.get("window_width", DEFAULT_WINDOW_WIDTH)

    @window_width.setter
    def window_width(self, value: int) -> None:
        """Set window width."""
        self._settings["window_width"] = value

    @property
    def window_height(self) -> int:
        """Get window height."""
        return self._settings.get("window_height", DEFAULT_WINDOW_HEIGHT)

    @window_height.setter
    def window_height(self, value: int) -> None:
        """Set window height."""
        self._settings["window_height"] = value

    @property
    def recent_files(self) -> list[str]:
        """Get list of recent files."""
        return self._settings.get("recent_files", [])

    @recent_files.setter
    def recent_files(self, value: list[str]) -> None:
        """Set recent files list."""
        self._settings["recent_files"] = value

    def add_recent_file(self, file_path: str) -> None:
        """
        Add a file to recent files list.

        Args:
            file_path: Path to the file.
        """
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)

        self.recent_files.insert(0, file_path)

        # Limit to 10 most recent
        self.recent_files = self.recent_files[:10]

    @property
    def sidebar_width(self) -> int:
        """Get sidebar width."""
        return self._settings.get("sidebar_width", 250)

    @sidebar_width.setter
    def sidebar_width(self, value: int) -> None:
        """Set sidebar width."""
        self._settings["sidebar_width"] = value

    @property
    def page_size(self) -> int:
        """Get page size for pagination."""
        return self._settings.get("page_size", 100)

    @page_size.setter
    def page_size(self, value: int) -> None:
        """Set page size."""
        self._settings["page_size"] = value

    def __enter__(self) -> "Settings":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager and save settings."""
        self.save()
