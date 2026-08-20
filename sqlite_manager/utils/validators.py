"""
Input validation utilities for SQLite Database Manager.

This module provides validation functions for user input to ensure security and data integrity.
"""

import re
from typing import Final

from core.exceptions import ValidationError


# Valid SQLite identifier pattern (table names, column names, etc.)
# Must start with letter or underscore, followed by alphanumeric or underscore
IDENTIFIER_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

# Reserved keywords in SQLite (partial list of common ones)
SQLITE_RESERVED_KEYWORDS: Final[set[str]] = {
    "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER",
    "TABLE", "INDEX", "VIEW", "TRIGGER", "DATABASE", "PRIMARY", "KEY",
    "FOREIGN", "REFERENCES", "CONSTRAINT", "DEFAULT", "NOT", "NULL",
    "UNIQUE", "CHECK", "ASC", "DESC", "ORDER", "BY", "GROUP", "HAVING",
    "WHERE", "FROM", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "ON",
    "AND", "OR", "IN", "BETWEEN", "LIKE", "IS", "LIMIT", "OFFSET",
    "INTEGER", "TEXT", "REAL", "BLOB", "NUMERIC", "AUTOINCREMENT",
    "CASCADE", "RESTRICT", "SET", "NO", "ACTION", "DEFERRABLE",
    "INITIALLY", "TRANSACTION", "COMMIT", "ROLLBACK", "BEGIN", "END",
    "VACUUM", "ANALYZE", "REINDEX", "PRAGMA", "ATTACH", "DETACH",
    "EXISTS", "CASE", "WHEN", "THEN", "ELSE", "AS", "DISTINCT", "ALL",
    "UNION", "INTERSECT", "EXCEPT", "NATURAL", "CROSS", "FULL",
    "VALUES", "INTO", "SET", "CURRENT_TIMESTAMP", "CURRENT_DATE",
    "CURRENT_TIME", "TRUE", "FALSE", "ROWID", "OID", "_ROWID_"
}

# Maximum lengths
MAX_TABLE_NAME_LENGTH: Final[int] = 64
MAX_COLUMN_NAME_LENGTH: Final[int] = 64
MAX_INDEX_NAME_LENGTH: Final[int] = 64


def validate_identifier(name: str, identifier_type: str = "Identifier") -> None:
    """
    Validate a database identifier (table name, column name, etc.).

    Args:
        name: The identifier to validate.
        identifier_type: Type of identifier for error messages.

    Raises:
        ValidationError: If the identifier is invalid.
    """
    if not name:
        raise ValidationError(f"{identifier_type} cannot be empty")

    if not IDENTIFIER_PATTERN.match(name):
        raise ValidationError(
            f"{identifier_type} '{name}' contains invalid characters. "
            "Use only letters, numbers, and underscores, starting with a letter or underscore."
        )

    if name.upper() in SQLITE_RESERVED_KEYWORDS:
        raise ValidationError(
            f"{identifier_type} '{name}' is a reserved keyword in SQLite"
        )


def validate_table_name(name: str) -> None:
    """
    Validate a table name.

    Args:
        name: The table name to validate.

    Raises:
        ValidationError: If the table name is invalid.
    """
    validate_identifier(name, "Table name")

    if len(name) > MAX_TABLE_NAME_LENGTH:
        raise ValidationError(
            f"Table name '{name}' exceeds maximum length of {MAX_TABLE_NAME_LENGTH} characters"
        )

    # Check for sqlite_ prefix (reserved for internal tables)
    if name.lower().startswith("sqlite_"):
        raise ValidationError(
            "Table names starting with 'sqlite_' are reserved for internal use"
        )


def validate_column_name(name: str) -> None:
    """
    Validate a column name.

    Args:
        name: The column name to validate.

    Raises:
        ValidationError: If the column name is invalid.
    """
    validate_identifier(name, "Column name")

    if len(name) > MAX_COLUMN_NAME_LENGTH:
        raise ValidationError(
            f"Column name '{name}' exceeds maximum length of {MAX_COLUMN_NAME_LENGTH} characters"
        )


def validate_index_name(name: str) -> None:
    """
    Validate an index name.

    Args:
        name: The index name to validate.

    Raises:
        ValidationError: If the index name is invalid.
    """
    validate_identifier(name, "Index name")

    if len(name) > MAX_INDEX_NAME_LENGTH:
        raise ValidationError(
            f"Index name '{name}' exceeds maximum length of {MAX_INDEX_NAME_LENGTH} characters"
        )


def validate_view_name(name: str) -> None:
    """
    Validate a view name.

    Args:
        name: The view name to validate.

    Raises:
        ValidationError: If the view name is invalid.
    """
    validate_identifier(name, "View name")

    if name.lower().startswith("sqlite_"):
        raise ValidationError(
            "View names starting with 'sqlite_' are reserved for internal use"
        )


def validate_trigger_name(name: str) -> None:
    """
    Validate a trigger name.

    Args:
        name: The trigger name to validate.

    Raises:
        ValidationError: If the trigger name is invalid.
    """
    validate_identifier(name, "Trigger name")


def validate_sqlite_type(data_type: str) -> bool:
    """
    Validate if a string is a valid SQLite data type.

    Args:
        data_type: The data type to validate.

    Returns:
        True if valid, False otherwise.
    """
    valid_types = {
        "INTEGER", "INT", "TINYINT", "SMALLINT", "MEDIUMINT", "BIGINT",
        "UNSIGNED BIG INT", "INT2", "INT8",
        "TEXT", "VARCHAR", "CHARACTER", "NVARCHAR", "NCHAR", "CLOB",
        "REAL", "DOUBLE", "DOUBLE PRECISION", "FLOAT",
        "BLOB",
        "NUMERIC", "DECIMAL", "BOOLEAN", "DATE", "DATETIME",
        "ANY"
    }

    return data_type.upper() in valid_types


def sanitize_identifier(name: str) -> str:
    """
    Sanitize an identifier by removing invalid characters.

    Args:
        name: The identifier to sanitize.

    Returns:
        Sanitized identifier.
    """
    # Remove any character that's not alphanumeric or underscore
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "", name)

    # Ensure it starts with a letter or underscore
    if sanitized and not sanitized[0].isalpha():
        sanitized = "_" + sanitized

    return sanitized or "unnamed"


def escape_sql_identifier(name: str) -> str:
    """
    Escape an SQL identifier using double quotes.

    Args:
        name: The identifier to escape.

    Returns:
        Escaped identifier safe for use in SQL queries.
    """
    # Double any existing double quotes
    escaped = name.replace('"', '""')
    return f'"{escaped}"'
