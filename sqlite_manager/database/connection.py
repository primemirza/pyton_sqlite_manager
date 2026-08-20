"""
Database connection management for SQLite Database Manager.

This module handles all database connections with proper lifecycle management,
transaction control, and error handling.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Any

from core.config import DEFAULT_LIMIT
from core.exceptions import DatabaseConnectionError, DatabaseOperationError, TransactionError
from utils.logger import get_logger


logger = get_logger(__name__)


class DatabaseConnection:
    """
    Manages SQLite database connections with proper lifecycle management.

    This class provides a centralized way to manage database connections,
    ensuring proper resource cleanup and transaction management.

    Attributes:
        db_path: Path to the SQLite database file.
        connection: Active SQLite connection object.
        foreign_keys_enabled: Whether foreign key constraints are enabled.
    """

    def __init__(self, db_path: Path | str) -> None:
        """
        Initialize database connection manager.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = Path(db_path) if isinstance(db_path, str) else db_path
        self._connection: sqlite3.Connection | None = None
        self._foreign_keys_enabled: bool = False
        logger.info(f"DatabaseConnection initialized for path: {self.db_path}")

    @property
    def connection(self) -> sqlite3.Connection:
        """
        Get the active database connection.

        Returns:
            Active SQLite connection.

        Raises:
            DatabaseConnectionError: If no connection is active.
        """
        if self._connection is None:
            raise DatabaseConnectionError("No active database connection")
        return self._connection

    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._connection is not None

    @property
    def foreign_keys_enabled(self) -> bool:
        """Check if foreign key constraints are enabled."""
        return self._foreign_keys_enabled

    def connect(self, enable_foreign_keys: bool = True) -> None:
        """
        Establish database connection.

        Args:
            enable_foreign_keys: Whether to enable foreign key constraints.

        Raises:
            DatabaseConnectionError: If connection fails.
        """
        try:
            logger.info(f"Connecting to database: {self.db_path}")
            self._connection = sqlite3.connect(
                str(self.db_path),
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                isolation_level=None  # Autocommit mode, we'll manage transactions manually
            )
            self._connection.row_factory = sqlite3.Row

            # Enable foreign keys if requested
            if enable_foreign_keys:
                self.enable_foreign_keys()

            logger.info(f"Successfully connected to database: {self.db_path}")

        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseConnectionError(
                f"Failed to connect to database",
                str(e)
            ) from e

    def disconnect(self) -> None:
        """
        Close database connection.

        Raises:
            DatabaseOperationError: If disconnection fails.
        """
        if self._connection:
            try:
                logger.info(f"Disconnecting from database: {self.db_path}")
                self._connection.close()
                self._connection = None
                self._foreign_keys_enabled = False
                logger.info("Successfully disconnected from database")
            except sqlite3.Error as e:
                logger.error(f"Error during disconnection: {e}")
                raise DatabaseOperationError(
                    "Failed to close database connection",
                    str(e)
                ) from e

    def enable_foreign_keys(self) -> None:
        """
        Enable foreign key constraints.

        Raises:
            DatabaseOperationError: If enabling foreign keys fails.
        """
        try:
            self.connection.execute("PRAGMA foreign_keys = ON")
            self._foreign_keys_enabled = True
            logger.debug("Foreign key constraints enabled")
        except sqlite3.Error as e:
            logger.error(f"Failed to enable foreign keys: {e}")
            raise DatabaseOperationError(
                "Failed to enable foreign key constraints",
                str(e)
            ) from e

    def disable_foreign_keys(self) -> None:
        """
        Disable foreign key constraints.

        Raises:
            DatabaseOperationError: If disabling foreign keys fails.
        """
        try:
            self.connection.execute("PRAGMA foreign_keys = OFF")
            self._foreign_keys_enabled = False
            logger.debug("Foreign key constraints disabled")
        except sqlite3.Error as e:
            logger.error(f"Failed to disable foreign keys: {e}")
            raise DatabaseOperationError(
                "Failed to disable foreign key constraints",
                str(e)
            ) from e

    def commit(self) -> None:
        """
        Commit current transaction.

        Raises:
            TransactionError: If commit fails.
        """
        try:
            self.connection.commit()
            logger.debug("Transaction committed")
        except sqlite3.Error as e:
            logger.error(f"Failed to commit transaction: {e}")
            raise TransactionError("Failed to commit transaction", str(e)) from e

    def rollback(self) -> None:
        """
        Rollback current transaction.

        Raises:
            TransactionError: If rollback fails.
        """
        try:
            self.connection.rollback()
            logger.debug("Transaction rolled back")
        except sqlite3.Error as e:
            logger.error(f"Failed to rollback transaction: {e}")
            raise TransactionError("Failed to rollback transaction", str(e)) from e

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        """
        Context manager for transaction management.

        Usage:
            with db.transaction():
                db.execute("INSERT INTO ...")
                db.execute("UPDATE ...")
            # Automatically commits on success, rolls back on error

        Yields:
            None

        Raises:
            TransactionError: If transaction management fails.
        """
        try:
            logger.debug("Starting transaction")
            yield
            self.commit()
            logger.debug("Transaction completed successfully")
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            self.rollback()
            raise

    def execute(
        self,
        query: str,
        parameters: tuple[Any, ...] | dict[str, Any] | None = None
    ) -> sqlite3.Cursor:
        """
        Execute a SQL query.

        Args:
            query: SQL query string.
            parameters: Query parameters (tuple or dict for named parameters).

        Returns:
            Cursor object with query results.

        Raises:
            DatabaseOperationError: If query execution fails.
        """
        try:
            cursor = self.connection.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            logger.debug(f"Executed query: {query[:100]}...")
            return cursor
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}\nQuery: {query}")
            raise DatabaseOperationError(
                "Failed to execute query",
                str(e)
            ) from e

    def executemany(
        self,
        query: str,
        parameters_list: list[tuple[Any, ...] | dict[str, Any]]
    ) -> sqlite3.Cursor:
        """
        Execute a SQL query with multiple parameter sets.

        Args:
            query: SQL query string.
            parameters_list: List of parameter tuples or dicts.

        Returns:
            Cursor object.

        Raises:
            DatabaseOperationError: If query execution fails.
        """
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, parameters_list)
            logger.debug(f"Executed query with {len(parameters_list)} parameter sets")
            return cursor
        except sqlite3.Error as e:
            logger.error(f"Bulk execution failed: {e}\nQuery: {query}")
            raise DatabaseOperationError(
                "Failed to execute bulk query",
                str(e)
            ) from e

    def fetchall(
        self,
        query: str,
        parameters: tuple[Any, ...] | dict[str, Any] | None = None
    ) -> list[sqlite3.Row]:
        """
        Execute query and fetch all results.

        Args:
            query: SQL query string.
            parameters: Query parameters.

        Returns:
            List of Row objects.
        """
        cursor = self.execute(query, parameters)
        return cursor.fetchall()

    def fetchone(
        self,
        query: str,
        parameters: tuple[Any, ...] | dict[str, Any] | None = None
    ) -> sqlite3.Row | None:
        """
        Execute query and fetch one result.

        Args:
            query: SQL query string.
            parameters: Query parameters.

        Returns:
            Row object or None if no results.
        """
        cursor = self.execute(query, parameters)
        return cursor.fetchone()

    def fetchmany(
        self,
        query: str,
        size: int = DEFAULT_LIMIT,
        parameters: tuple[Any, ...] | dict[str, Any] | None = None
    ) -> list[sqlite3.Row]:
        """
        Execute query and fetch a limited number of results.

        Args:
            query: SQL query string.
            size: Number of rows to fetch.
            parameters: Query parameters.

        Returns:
            List of Row objects.
        """
        cursor = self.execute(query, parameters)
        return cursor.fetchmany(size)

    def get_table_count(self) -> int:
        """
        Get the number of tables in the database.

        Returns:
            Number of user tables.
        """
        query = """
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        result = self.fetchone(query)
        return result[0] if result else 0

    def get_view_count(self) -> int:
        """
        Get the number of views in the database.

        Returns:
            Number of views.
        """
        query = "SELECT COUNT(*) FROM sqlite_master WHERE type='view'"
        result = self.fetchone(query)
        return result[0] if result else 0

    def get_index_count(self) -> int:
        """
        Get the number of indexes in the database.

        Returns:
            Number of user indexes.
        """
        query = """
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """
        result = self.fetchone(query)
        return result[0] if result else 0

    def get_trigger_count(self) -> int:
        """
        Get the number of triggers in the database.

        Returns:
            Number of triggers.
        """
        query = "SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'"
        result = self.fetchone(query)
        return result[0] if result else 0

    def __enter__(self) -> "DatabaseConnection":
        """Connect when entering context."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Disconnect when exiting context."""
        self.disconnect()

    def __del__(self) -> None:
        """Ensure connection is closed on deletion."""
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
