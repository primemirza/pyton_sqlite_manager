"""
Database manager for SQLite Database Manager.

This module provides high-level database operations and management functions.
"""

import sqlite3
from pathlib import Path
from typing import Any

from core.config import SUPPORTED_EXTENSIONS
from core.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    TableNotFoundError,
    BackupError,
    RestoreError,
)
from database.connection import DatabaseConnection
from utils.logger import get_logger
from utils.validators import validate_table_name


logger = get_logger(__name__)


class DatabaseManager:
    """
    High-level database management operations.

    This class provides methods for common database operations like
    creating databases, backup, restore, vacuum, analyze, etc.

    Attributes:
        connection: DatabaseConnection instance.
    """

    def __init__(self, db_path: Path | str | None = None) -> None:
        """
        Initialize database manager.

        Args:
            db_path: Optional path to database file.
        """
        self._connection: DatabaseConnection | None = None
        if db_path:
            self._connection = DatabaseConnection(db_path)

    @property
    def connection(self) -> DatabaseConnection:
        """Get the database connection."""
        if self._connection is None:
            raise DatabaseConnectionError("No database connection established")
        return self._connection

    @property
    def db_path(self) -> Path | None:
        """Get the database file path."""
        return self._connection.db_path if self._connection else None

    @property
    def is_connected(self) -> bool:
        """Check if connected to a database."""
        return self._connection is not None and self._connection.is_connected

    def create_database(self, db_path: Path | str) -> "DatabaseManager":
        """
        Create a new SQLite database.

        Args:
            db_path: Path where database should be created.

        Returns:
            Self for method chaining.

        Raises:
            DatabaseOperationError: If database creation fails.
        """
        db_path = Path(db_path) if isinstance(db_path, str) else db_path

        # Validate extension
        if db_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            logger.warning(f"Unusual file extension for database: {db_path.suffix}")

        try:
            logger.info(f"Creating new database at: {db_path}")
            # Create parent directories if they don't exist
            db_path.parent.mkdir(parents=True, exist_ok=True)

            # Create connection which will create the file
            self._connection = DatabaseConnection(db_path)
            self._connection.connect()

            logger.info(f"Database created successfully: {db_path}")
            return self

        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            raise DatabaseOperationError(
                f"Failed to create database at {db_path}",
                str(e)
            ) from e

    def open_database(self, db_path: Path | str, enable_foreign_keys: bool = True) -> "DatabaseManager":
        """
        Open an existing SQLite database.

        Args:
            db_path: Path to database file.
            enable_foreign_keys: Whether to enable foreign key constraints.

        Returns:
            Self for method chaining.

        Raises:
            DatabaseConnectionError: If opening database fails.
        """
        db_path = Path(db_path) if isinstance(db_path, str) else db_path

        if not db_path.exists():
            raise DatabaseConnectionError(
                f"Database file does not exist: {db_path}"
            )

        try:
            logger.info(f"Opening database: {db_path}")
            self._connection = DatabaseConnection(db_path)
            self._connection.connect(enable_foreign_keys=enable_foreign_keys)
            logger.info(f"Database opened successfully: {db_path}")
            return self

        except Exception as e:
            logger.error(f"Failed to open database: {e}")
            raise DatabaseConnectionError(
                f"Failed to open database {db_path}",
                str(e)
            ) from e

    def close_database(self) -> None:
        """Close the current database connection."""
        if self._connection:
            logger.info(f"Closing database: {self._connection.db_path}")
            self._connection.disconnect()
            self._connection = None
            logger.info("Database closed")

    def get_sqlite_version(self) -> str:
        """
        Get SQLite version.

        Returns:
            SQLite version string.
        """
        query = "SELECT sqlite_version()"
        result = self.connection.fetchone(query)
        return result[0] if result else "Unknown"

    def get_database_info(self) -> dict[str, Any]:
        """
        Get comprehensive database information.

        Returns:
            Dictionary with database information.
        """
        info: dict[str, Any] = {}

        if not self.is_connected or self.db_path is None:
            return info

        try:
            # File info
            info["path"] = str(self.db_path.absolute())
            info["size"] = self.db_path.stat().st_size
            info["size_formatted"] = self._format_file_size(info["size"])

            # SQLite version
            info["sqlite_version"] = self.get_sqlite_version()

            # Counts
            info["table_count"] = self.connection.get_table_count()
            info["view_count"] = self.connection.get_view_count()
            info["index_count"] = self.connection.get_index_count()
            info["trigger_count"] = self.connection.get_trigger_count()

            # Pragmas
            info["page_size"] = self._get_pragma("page_size")
            info["page_count"] = self._get_pragma("page_count")
            info["encoding"] = self._get_pragma("encoding")
            info["journal_mode"] = self._get_pragma("journal_mode")
            info["foreign_keys"] = 1 if self.connection.foreign_keys_enabled else 0
            info["auto_vacuum"] = self._get_pragma("auto_vacuum")
            info["user_version"] = self._get_pragma("user_version")

            # Calculate size from pages
            if info["page_size"] and info["page_count"]:
                info["calculated_size"] = info["page_size"] * info["page_count"]

        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            info["error"] = str(e)

        return info

    def _get_pragma(self, pragma_name: str) -> Any:
        """
        Get a PRAGMA value.

        Args:
            pragma_name: Name of the pragma.

        Returns:
            Pragma value or None.
        """
        try:
            query = f"PRAGMA {pragma_name}"
            result = self.connection.fetchone(query)
            return result[0] if result else None
        except Exception:
            return None

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    def backup_database(self, backup_path: Path | str) -> None:
        """
        Create a backup of the database using SQLite backup API.

        Args:
            backup_path: Path for backup file.

        Raises:
            BackupError: If backup fails.
        """
        if not self.is_connected:
            raise BackupError("No database connection to backup")

        backup_path = Path(backup_path) if isinstance(backup_path, str) else backup_path

        try:
            logger.info(f"Starting database backup to: {backup_path}")

            # Create backup using SQLite API
            backup_db = sqlite3.connect(str(backup_path))
            self.connection.connection.backup(backup_db)
            backup_db.close()

            logger.info(f"Database backup completed: {backup_path}")

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise BackupError(
                f"Failed to backup database",
                str(e)
            ) from e

    def restore_database(self, backup_path: Path | str) -> None:
        """
        Restore database from a backup file.

        Args:
            backup_path: Path to backup file.

        Raises:
            RestoreError: If restore fails.
        """
        if not self.is_connected or self.db_path is None:
            raise RestoreError("No database connection to restore")

        backup_path = Path(backup_path) if isinstance(backup_path, str) else backup_path

        if not backup_path.exists():
            raise RestoreError(f"Backup file does not exist: {backup_path}")

        try:
            logger.info(f"Restoring database from backup: {backup_path}")

            # Close current connection
            self.close_database()

            # Remove current database
            if self.db_path.exists():
                self.db_path.unlink()

            # Copy backup to database location
            import shutil
            shutil.copy2(str(backup_path), str(self.db_path))

            # Reopen database
            self.open_database(self.db_path)

            logger.info(f"Database restored successfully from: {backup_path}")

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise RestoreError(
                f"Failed to restore database from backup",
                str(e)
            ) from e

    def vacuum_database(self) -> None:
        """
        Vacuum the database to reclaim space.

        Raises:
            DatabaseOperationError: If vacuum fails.
        """
        try:
            logger.info("Vacuuming database")
            self.connection.execute("VACUUM")
            logger.info("Database vacuum completed")
        except Exception as e:
            logger.error(f"Vacuum failed: {e}")
            raise DatabaseOperationError("Failed to vacuum database", str(e)) from e

    def analyze_database(self) -> None:
        """
        Analyze the database to optimize query performance.

        Raises:
            DatabaseOperationError: If analyze fails.
        """
        try:
            logger.info("Analyzing database")
            self.connection.execute("ANALYZE")
            logger.info("Database analysis completed")
        except Exception as e:
            logger.error(f"Analyze failed: {e}")
            raise DatabaseOperationError("Failed to analyze database", str(e)) from e

    def integrity_check(self) -> list[str]:
        """
        Run integrity check on the database.

        Returns:
            List of issues found (empty if database is OK).

        Raises:
            DatabaseOperationError: If check fails.
        """
        try:
            logger.info("Running integrity check")
            result = self.connection.fetchall("PRAGMA integrity_check")

            issues = []
            for row in result:
                if row[0] != "ok":
                    issues.append(row[0])

            if issues:
                logger.warning(f"Integrity check found {len(issues)} issue(s)")
            else:
                logger.info("Integrity check passed")

            return issues

        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
            raise DatabaseOperationError("Failed to run integrity check", str(e)) from e

    def get_tables(self) -> list[str]:
        """
        Get list of all user tables.

        Returns:
            List of table names.
        """
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        result = self.connection.fetchall(query)
        return [row[0] for row in result]

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.

        Args:
            table_name: Name of the table.

        Returns:
            True if table exists.
        """
        return table_name in self.get_tables()

    def get_table_info(self, table_name: str) -> list[dict[str, Any]]:
        """
        Get column information for a table.

        Args:
            table_name: Name of the table.

        Returns:
            List of column information dictionaries.
        """
        validate_table_name(table_name)

        query = f"PRAGMA table_info({table_name})"
        result = self.connection.fetchall(query)

        columns = []
        for row in result:
            columns.append({
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "notnull": bool(row[3]),
                "default_value": row[4],
                "pk": bool(row[5])
            })

        return columns

    def get_foreign_keys(self, table_name: str) -> list[dict[str, Any]]:
        """
        Get foreign key information for a table.

        Args:
            table_name: Name of the table.

        Returns:
            List of foreign key information dictionaries.
        """
        validate_table_name(table_name)

        query = f"PRAGMA foreign_key_list({table_name})"
        result = self.connection.fetchall(query)

        foreign_keys = []
        for row in result:
            foreign_keys.append({
                "id": row[0],
                "seq": row[1],
                "table": row[2],
                "from": row[3],
                "to": row[4],
                "on_update": row[5],
                "on_delete": row[6],
                "match": row[7]
            })

        return foreign_keys

    def get_indexes(self, table_name: str) -> list[dict[str, Any]]:
        """
        Get index information for a table.

        Args:
            table_name: Name of the table.

        Returns:
            List of index information dictionaries.
        """
        validate_table_name(table_name)

        query = f"PRAGMA index_list({table_name})"
        result = self.connection.fetchall(query)

        indexes = []
        for row in result:
            indexes.append({
                "seq": row[0],
                "name": row[1],
                "unique": bool(row[2]),
                "origin": row[3],
                "partial": bool(row[4]) if len(row) > 4 else False
            })

        return indexes

    def get_index_columns(self, index_name: str) -> list[dict[str, Any]]:
        """
        Get columns for an index.

        Args:
            index_name: Name of the index.

        Returns:
            List of index column information.
        """
        query = f"PRAGMA index_info({index_name})"
        result = self.connection.fetchall(query)

        columns = []
        for row in result:
            columns.append({
                "seqno": row[0],
                "cid": row[1],
                "name": row[2]
            })

        return columns

    def get_triggers(self, table_name: str | None = None) -> list[dict[str, Any]]:
        """
        Get trigger information.

        Args:
            table_name: Optional table name to filter triggers.

        Returns:
            List of trigger information dictionaries.
        """
        query = """
            SELECT name, tbl_name, sql FROM sqlite_master
            WHERE type='trigger'
        """

        if table_name:
            validate_table_name(table_name)
            query += f" AND tbl_name = '{table_name}'"

        query += " ORDER BY name"

        result = self.connection.fetchall(query)

        triggers = []
        for row in result:
            triggers.append({
                "name": row[0],
                "table": row[1],
                "sql": row[2]
            })

        return triggers

    def get_views(self) -> list[dict[str, Any]]:
        """
        Get view information.

        Returns:
            List of view information dictionaries.
        """
        query = """
            SELECT name, sql FROM sqlite_master
            WHERE type='view'
            ORDER BY name
        """
        result = self.connection.fetchall(query)

        views = []
        for row in result:
            views.append({
                "name": row[0],
                "sql": row[1]
            })

        return views

    def get_all_indexes(self) -> list[dict[str, Any]]:
        """
        Get all indexes in the database.

        Returns:
            List of index information dictionaries.
        """
        query = """
            SELECT name, tbl_name, sql FROM sqlite_master
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        result = self.connection.fetchall(query)

        indexes = []
        for row in result:
            indexes.append({
                "name": row[0],
                "table": row[1],
                "sql": row[2]
            })

        return indexes
