"""
Main window for SQLite Database Manager.

This module contains the main application window with all primary UI components.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QToolBar,
    QStatusBar,
    QMenuBar,
    QMenu,
    QAction,
    QFileDialog,
    QMessageBox,
    QLabel,
    QFrame,
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QKeySequence

from core.config import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
)
from database.manager import DatabaseManager
from app.settings import Settings
from utils.logger import get_logger


logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window.

    This is the primary window containing all UI components:
    - Menu bar
    - Toolbar
    - Sidebar (database explorer)
    - Main content area
    - Status bar

    Signals:
        database_opened: Emitted when a database is opened.
        database_closed: Emitted when a database is closed.
    """

    database_opened = Signal(str)  # path
    database_closed = Signal()

    def __init__(self, parent=None) -> None:
        """
        Initialize main window.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)

        self._db_manager = DatabaseManager()
        self._settings = Settings()
        self._current_file: Path | None = None

        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._apply_theme()

        logger.info("Main window initialized")

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Splitter for sidebar and main area
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Sidebar placeholder
        self._sidebar = QFrame()
        self._sidebar.setMinimumWidth(150)
        self._sidebar.setMaximumWidth(500)
        self._sidebar.setStyleSheet("QFrame { background-color: #f0f0f0; }")
        sidebar_label = QLabel("Database Explorer\n(Coming in Phase 4)")
        sidebar_label.setAlignment(Qt.AlignCenter)
        sidebar_layout = QVBoxLayout(self._sidebar)
        sidebar_layout.addWidget(sidebar_label)
        splitter.addWidget(self._sidebar)

        # Main content area placeholder
        self._main_content = QFrame()
        self._main_content.setStyleSheet("QFrame { background-color: white; }")
        content_label = QLabel(
            "Welcome to SQLite Database Manager\n\n"
            "Open or create a database to get started\n"
            "Use File > New Database or File > Open Database"
        )
        content_label.setAlignment(Qt.AlignCenter)
        content_layout = QVBoxLayout(self._main_content)
        content_layout.addWidget(content_label)
        splitter.addWidget(self._main_content)

        # Set splitter sizes
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([250, 950])

    def _setup_menu(self) -> None:
        """Set up menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        self._action_new_db = QAction("&New Database", self)
        self._action_new_db.setShortcut(QKeySequence.New)
        self._action_new_db.setStatusTip("Create a new database")
        self._action_new_db.triggered.connect(self._new_database)
        file_menu.addAction(self._action_new_db)

        self._action_open_db = QAction("&Open Database", self)
        self._action_open_db.setShortcut(QKeySequence.Open)
        self._action_open_db.setStatusTip("Open an existing database")
        self._action_open_db.triggered.connect(self._open_database)
        file_menu.addAction(self._action_open_db)

        file_menu.addSeparator()

        self._action_close_db = QAction("&Close Database", self)
        self._action_close_db.setShortcut("Ctrl+W")
        self._action_close_db.setStatusTip("Close current database")
        self._action_close_db.setEnabled(False)
        self._action_close_db.triggered.connect(self._close_database)
        file_menu.addAction(self._action_close_db)

        file_menu.addSeparator()

        self._action_exit = QAction("E&xit", self)
        self._action_exit.setShortcut(QKeySequence.Quit)
        self._action_exit.setStatusTip("Exit application")
        self._action_exit.triggered.connect(self.close)
        file_menu.addAction(self._action_exit)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        self._action_refresh = QAction("&Refresh", self)
        self._action_refresh.setShortcut(QKeySequence.Refresh)
        self._action_refresh.setStatusTip("Refresh database structure")
        self._action_refresh.setEnabled(False)
        self._action_refresh.triggered.connect(self._refresh)
        edit_menu.addAction(self._action_refresh)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        self._action_backup = QAction("&Backup Database", self)
        self._action_backup.setStatusTip("Create a backup of the database")
        self._action_backup.setEnabled(False)
        self._action_backup.triggered.connect(self._backup_database)
        tools_menu.addAction(self._action_backup)

        self._action_vacuum = QAction("&Vacuum Database", self)
        self._action_vacuum.setStatusTip("Vacuum the database to reclaim space")
        self._action_vacuum.setEnabled(False)
        self._action_vacuum.triggered.connect(self._vacuum_database)
        tools_menu.addAction(self._action_vacuum)

        self._action_analyze = QAction("&Analyze Database", self)
        self._action_analyze.setStatusTip("Analyze database for optimization")
        self._action_analyze.setEnabled(False)
        self._action_analyze.triggered.connect(self._analyze_database)
        tools_menu.addAction(self._action_analyze)

        self._action_integrity = QAction("&Integrity Check", self)
        self._action_integrity.setStatusTip("Run integrity check on database")
        self._action_integrity.setEnabled(False)
        self._action_integrity.triggered.connect(self._integrity_check)
        tools_menu.addAction(self._action_integrity)

        # View menu
        view_menu = menubar.addMenu("&View")

        self._action_toggle_theme = QAction("Toggle &Dark Mode", self)
        self._action_toggle_theme.setStatusTip("Toggle between light and dark theme")
        self._action_toggle_theme.triggered.connect(self._toggle_theme)
        view_menu.addAction(self._action_toggle_theme)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        self._action_about = QAction("&About", self)
        self._action_about.setStatusTip("About SQLite Database Manager")
        self._action_about.triggered.connect(self._show_about)
        help_menu.addAction(self._action_about)

    def _setup_toolbar(self) -> None:
        """Set up toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # New Database
        action_new = QAction("New", self)
        action_new.setStatusTip("Create new database")
        action_new.triggered.connect(self._new_database)
        toolbar.addAction(action_new)

        # Open Database
        action_open = QAction("Open", self)
        action_open.setStatusTip("Open database")
        action_open.triggered.connect(self._open_database)
        toolbar.addAction(action_open)

        # Close Database
        self._toolbar_close = QAction("Close", self)
        self._toolbar_close.setStatusTip("Close database")
        self._toolbar_close.setEnabled(False)
        self._toolbar_close.triggered.connect(self._close_database)
        toolbar.addAction(self._toolbar_close)

        toolbar.addSeparator()

        # Refresh
        self._toolbar_refresh = QAction("Refresh", self)
        self._toolbar_refresh.setStatusTip("Refresh")
        self._toolbar_refresh.setEnabled(False)
        self._toolbar_refresh.triggered.connect(self._refresh)
        toolbar.addAction(self._toolbar_refresh)

        toolbar.addSeparator()

        # Backup
        self._toolbar_backup = QAction("Backup", self)
        self._toolbar_backup.setStatusTip("Backup database")
        self._toolbar_backup.setEnabled(False)
        self._toolbar_backup.triggered.connect(self._backup_database)
        toolbar.addAction(self._toolbar_backup)

    def _setup_statusbar(self) -> None:
        """Set up status bar."""
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)

        # Database path label
        self._status_db_path = QLabel("No database open")
        self._statusbar.addWidget(self._status_db_path)

        # Spacer
        self._statusbar.addPermanentWidget(QWidget(), 1)

        # Database info label
        self._status_db_info = QLabel("")
        self._statusbar.addPermanentWidget(self._status_db_info)

    def _apply_theme(self) -> None:
        """Apply current theme."""
        theme = self._settings.theme
        # Theme implementation will be added in Phase 13
        logger.debug(f"Theme applied: {theme}")

    def _update_ui_state(self, has_database: bool) -> None:
        """
        Update UI state based on database connection.

        Args:
            has_database: Whether a database is currently open.
        """
        # Menu actions
        self._action_close_db.setEnabled(has_database)
        self._action_refresh.setEnabled(has_database)
        self._action_backup.setEnabled(has_database)
        self._action_vacuum.setEnabled(has_database)
        self._action_analyze.setEnabled(has_database)
        self._action_integrity.setEnabled(has_database)

        # Toolbar actions
        self._toolbar_close.setEnabled(has_database)
        self._toolbar_refresh.setEnabled(has_database)
        self._toolbar_backup.setEnabled(has_database)

    def _new_database(self) -> None:
        """Create a new database."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Create New Database",
            str(Path.home()),
            "SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*)"
        )

        if not file_path:
            return

        try:
            db_path = Path(file_path)

            # Close existing database
            if self._db_manager.is_connected:
                self._close_database()

            # Create new database
            self._db_manager.create_database(db_path)
            self._current_file = db_path

            # Update UI
            self._update_ui_state(True)
            self._status_db_path.setText(f"Database: {db_path}")
            self._status_db_info.setText("New database created")

            # Add to recent files
            self._settings.add_recent_file(str(db_path))

            self.database_opened.emit(str(db_path))
            logger.info(f"New database created: {db_path}")

            QMessageBox.information(
                self,
                "Database Created",
                f"New database created successfully:\n{db_path}"
            )

        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create database:\n{str(e)}"
            )

    def _open_database(self) -> None:
        """Open an existing database."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Database",
            str(Path.home()),
            "SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*)"
        )

        if not file_path:
            return

        try:
            db_path = Path(file_path)

            # Close existing database
            if self._db_manager.is_connected:
                self._close_database()

            # Open database
            self._db_manager.open_database(db_path)
            self._current_file = db_path

            # Update UI
            self._update_ui_state(True)
            self._status_db_path.setText(f"Database: {db_path}")

            # Get database info
            info = self._db_manager.get_database_info()
            size_str = info.get("size_formatted", "Unknown")
            table_count = info.get("table_count", 0)
            self._status_db_info.setText(f"{size_str} | {table_count} tables")

            # Add to recent files
            self._settings.add_recent_file(str(db_path))

            self.database_opened.emit(str(db_path))
            logger.info(f"Database opened: {db_path}")

        except Exception as e:
            logger.error(f"Failed to open database: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open database:\n{str(e)}"
            )

    def _close_database(self) -> None:
        """Close current database."""
        if not self._db_manager.is_connected:
            return

        try:
            self._db_manager.close_database()
            self._current_file = None

            # Update UI
            self._update_ui_state(False)
            self._status_db_path.setText("No database open")
            self._status_db_info.setText("")

            self.database_closed.emit()
            logger.info("Database closed")

        except Exception as e:
            logger.error(f"Failed to close database: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to close database:\n{str(e)}"
            )

    def _refresh(self) -> None:
        """Refresh database view."""
        if not self._db_manager.is_connected:
            return

        logger.debug("Refreshing database view")
        # Implementation will be added in Phase 4
        self._statusbar.showMessage("Database refreshed", 2000)

    def _backup_database(self) -> None:
        """Backup current database."""
        if not self._db_manager.is_connected or not self._current_file:
            return

        default_backup = self._current_file.with_suffix(".backup.db")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Backup Database",
            str(default_backup),
            "SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*)"
        )

        if not file_path:
            return

        try:
            self._db_manager.backup_database(Path(file_path))
            logger.info(f"Database backed up to: {file_path}")
            QMessageBox.information(
                self,
                "Backup Complete",
                f"Database backed up successfully:\n{file_path}"
            )

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            QMessageBox.critical(
                self,
                "Backup Failed",
                f"Failed to backup database:\n{str(e)}"
            )

    def _vacuum_database(self) -> None:
        """Vacuum current database."""
        if not self._db_manager.is_connected:
            return

        reply = QMessageBox.question(
            self,
            "Vacuum Database",
            "Vacuum reclaims unused space. This may take a while for large databases.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            self._db_manager.vacuum_database()
            logger.info("Database vacuum completed")
            self._statusbar.showMessage("Database vacuumed", 3000)

        except Exception as e:
            logger.error(f"Vacuum failed: {e}")
            QMessageBox.critical(
                self,
                "Vacuum Failed",
                f"Failed to vacuum database:\n{str(e)}"
            )

    def _analyze_database(self) -> None:
        """Analyze current database."""
        if not self._db_manager.is_connected:
            return

        try:
            self._db_manager.analyze_database()
            logger.info("Database analysis completed")
            self._statusbar.showMessage("Database analyzed", 3000)

        except Exception as e:
            logger.error(f"Analyze failed: {e}")
            QMessageBox.critical(
                self,
                "Analyze Failed",
                f"Failed to analyze database:\n{str(e)}"
            )

    def _integrity_check(self) -> None:
        """Run integrity check on current database."""
        if not self._db_manager.is_connected:
            return

        try:
            issues = self._db_manager.integrity_check()

            if issues:
                msg = f"Integrity check found {len(issues)} issue(s):\n\n"
                msg += "\n".join(issues[:10])  # Show first 10 issues
                if len(issues) > 10:
                    msg += f"\n... and {len(issues) - 10} more"
                QMessageBox.warning(self, "Integrity Issues", msg)
            else:
                QMessageBox.information(
                    self,
                    "Integrity Check",
                    "Database integrity check passed. No issues found."
                )

            logger.info(f"Integrity check completed, issues: {len(issues)}")

        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
            QMessageBox.critical(
                self,
                "Integrity Check Failed",
                f"Failed to run integrity check:\n{str(e)}"
            )

    def _toggle_theme(self) -> None:
        """Toggle between light and dark theme."""
        current = self._settings.theme
        new_theme = "dark" if current == "light" else "light"
        self._settings.theme = new_theme
        self._apply_theme()
        logger.info(f"Theme changed to: {new_theme}")

    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About SQLite Database Manager",
            f"<h2>SQLite Database Manager</h2>"
            f"<p>Version: {APP_VERSION}</p>"
            f"<p>A professional desktop application for managing SQLite databases.</p>"
            f"<p>Built with Python and PySide6.</p>"
        )

    def closeEvent(self, event) -> None:
        """
        Handle window close event.

        Args:
            event: Close event.
        """
        # Save settings
        self._settings.window_width = self.width()
        self._settings.window_height = self.height()
        self._settings.save()

        # Close database if open
        if self._db_manager.is_connected:
            self._close_database()

        logger.info("Main window closing")
        event.accept()
