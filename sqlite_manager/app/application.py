"""
Main application class for SQLite Database Manager.

This module contains the main application entry point and lifecycle management.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QCoreApplication

from core.config import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    ensure_directories,
)
from core.exceptions import ConfigurationError
from app.settings import Settings
from utils.logger import setup_logger, get_logger


logger = get_logger(__name__)


class Application(QApplication):
    """
    Main application class.

    This class extends QApplication and manages the application lifecycle,
    including initialization, settings, and shutdown.

    Attributes:
        settings: Application settings instance.
        main_window: Main window instance (created later).
    """

    def __init__(self, argv: list[str]) -> None:
        """
        Initialize the application.

        Args:
            argv: Command line arguments.
        """
        # Ensure directories exist before anything else
        ensure_directories()

        # Set up logging
        self._logger = setup_logger("sqlite_manager.app")

        # Enable High DPI scaling
        try:
            QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        except AttributeError:
            pass  # Qt6 handles this differently

        super().__init__(argv)

        # Set application metadata
        self.setApplicationName(APP_NAME)
        self.setApplicationVersion(APP_VERSION)
        self.setOrganizationName("SQLiteManager")
        self.setOrganizationDomain("sqlitemanager.local")

        # Initialize settings
        self._settings = Settings()

        # Apply settings
        self._apply_settings()

        # Main window will be created later
        self._main_window = None

        self._logger.info(f"{APP_NAME} v{APP_VERSION} initialized")

    def _apply_settings(self) -> None:
        """Apply application settings."""
        # Theme will be applied when main window is created
        pass

    @property
    def settings(self) -> Settings:
        """Get application settings."""
        return self._settings

    @property
    def main_window(self):
        """Get main window instance."""
        return self._main_window

    @main_window.setter
    def main_window(self, value) -> None:
        """Set main window instance."""
        self._main_window = value

    def run(self) -> int:
        """
        Run the application.

        Returns:
            Application exit code.
        """
        try:
            self._logger.info("Starting application")
            return self.exec()
        except Exception as e:
            self._logger.error(f"Application error: {e}", exc_info=True)
            return 1
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        """Clean up resources before shutdown."""
        self._logger.info("Shutting down application")

        # Save settings
        try:
            self._settings.save()
        except Exception as e:
            self._logger.error(f"Failed to save settings on shutdown: {e}")

        # Close main window if exists
        if self._main_window:
            try:
                self._main_window.close()
            except Exception as e:
                self._logger.error(f"Error closing main window: {e}")

    def set_theme(self, theme: str) -> None:
        """
        Set application theme.

        Args:
            theme: Theme name ('light' or 'dark').
        """
        self._settings.theme = theme
        # Stylesheet will be applied by main window

    def get_default_window_geometry(self) -> tuple[int, int, int, int]:
        """
        Get default window geometry.

        Returns:
            Tuple of (x, y, width, height).
        """
        width = min(
            max(self._settings.window_width, MIN_WINDOW_WIDTH),
            DEFAULT_WINDOW_WIDTH * 2
        )
        height = min(
            max(self._settings.window_height, MIN_WINDOW_HEIGHT),
            DEFAULT_WINDOW_HEIGHT * 2
        )

        # Center on screen
        from PySide6.QtGui import QScreen
        screen: QScreen = self.primaryScreen()
        screen_geometry = screen.availableGeometry()

        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2

        return (x, y, width, height)


def create_application(argv: list[str] | None = None) -> Application:
    """
    Create and configure the application instance.

    Args:
        argv: Optional command line arguments.

    Returns:
        Configured Application instance.
    """
    if argv is None:
        argv = sys.argv

    return Application(argv)


def main() -> int:
    """
    Main entry point for the application.

    Returns:
        Application exit code.
    """
    # Create application
    app = create_application()

    # Import and create main window here to avoid circular imports
    from ui.main_window import MainWindow

    main_window = MainWindow()
    app.main_window = main_window

    # Show main window
    main_window.show()

    # Run application
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
