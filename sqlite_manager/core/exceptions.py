"""
Custom exceptions for SQLite Database Manager.

This module defines application-specific exceptions for better error handling.
"""


class DatabaseManagerError(Exception):
    """Base exception for database manager errors."""

    def __init__(self, message: str, details: str | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}\n\nDetails: {self.details}"
        return self.message


class DatabaseConnectionError(DatabaseManagerError):
    """Exception raised when database connection fails."""

    pass


class DatabaseOperationError(DatabaseManagerError):
    """Exception raised when a database operation fails."""

    pass


class TableNotFoundError(DatabaseManagerError):
    """Exception raised when a table is not found."""

    pass


class ViewNotFoundError(DatabaseManagerError):
    """Exception raised when a view is not found."""

    pass


class IndexNotFoundError(DatabaseManagerError):
    """Exception raised when an index is not found."""

    pass


class TriggerNotFoundError(DatabaseManagerError):
    """Exception raised when a trigger is not found."""

    pass


class QueryExecutionError(DatabaseManagerError):
    """Exception raised when SQL query execution fails."""

    pass


class TransactionError(DatabaseManagerError):
    """Exception raised when transaction management fails."""

    pass


class BackupError(DatabaseManagerError):
    """Exception raised when backup operation fails."""

    pass


class RestoreError(DatabaseManagerError):
    """Exception raised when restore operation fails."""

    pass


class ImportError(DatabaseManagerError):
    """Exception raised when data import fails."""

    pass


class ExportError(DatabaseManagerError):
    """Exception raised when data export fails."""

    pass


class ValidationError(DatabaseManagerError):
    """Exception raised when input validation fails."""

    pass


class ConfigurationError(DatabaseManagerError):
    """Exception raised when configuration is invalid or missing."""

    pass
