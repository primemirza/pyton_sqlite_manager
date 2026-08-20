"""
Database module for SQLite Database Manager.

This module provides database connection and management functionality.
"""

from database.connection import DatabaseConnection
from database.manager import DatabaseManager

__all__ = ["DatabaseConnection", "DatabaseManager"]