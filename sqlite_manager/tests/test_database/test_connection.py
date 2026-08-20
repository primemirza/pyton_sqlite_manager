"""
Unit tests for database connection module.
"""

import pytest
from pathlib import Path
import tempfile
import os

from database.connection import DatabaseConnection
from core.exceptions import DatabaseConnectionError, DatabaseOperationError


class TestDatabaseConnection:
    """Test cases for DatabaseConnection class."""

    @pytest.fixture
    def temp_db_path(self) -> Path:
        """Create a temporary database file path."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = Path(f.name)
        yield db_path
        # Cleanup
        if db_path.exists():
            db_path.unlink()

    @pytest.fixture
    def connected_db(self, temp_db_path: Path) -> DatabaseConnection:
        """Create a connected database connection."""
        conn = DatabaseConnection(temp_db_path)
        conn.connect()
        yield conn
        conn.disconnect()

    def test_init(self, temp_db_path: Path) -> None:
        """Test DatabaseConnection initialization."""
        conn = DatabaseConnection(temp_db_path)
        assert conn.db_path == temp_db_path
        assert not conn.is_connected
        assert not conn.foreign_keys_enabled

    def test_connect(self, temp_db_path: Path) -> None:
        """Test database connection."""
        conn = DatabaseConnection(temp_db_path)
        conn.connect()
        assert conn.is_connected
        assert conn.foreign_keys_enabled  # Default is True
        conn.disconnect()

    def test_connect_without_foreign_keys(self, temp_db_path: Path) -> None:
        """Test connection without foreign keys."""
        conn = DatabaseConnection(temp_db_path)
        conn.connect(enable_foreign_keys=False)
        assert conn.is_connected
        assert not conn.foreign_keys_enabled
        conn.disconnect()

    def test_disconnect(self, temp_db_path: Path) -> None:
        """Test database disconnection."""
        conn = DatabaseConnection(temp_db_path)
        conn.connect()
        assert conn.is_connected
        conn.disconnect()
        assert not conn.is_connected

    def test_connection_property_raises_when_not_connected(self, temp_db_path: Path) -> None:
        """Test that accessing connection when not connected raises error."""
        conn = DatabaseConnection(temp_db_path)
        with pytest.raises(DatabaseConnectionError):
            _ = conn.connection

    def test_execute_query(self, connected_db: DatabaseConnection) -> None:
        """Test query execution."""
        # Create a test table
        connected_db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        
        # Insert data
        connected_db.execute("INSERT INTO test (name) VALUES (?)", ("test_name",))
        
        # Query data
        result = connected_db.fetchall("SELECT * FROM test")
        assert len(result) == 1
        assert result[0]["name"] == "test_name"

    def test_execute_with_parameters(self, connected_db: DatabaseConnection) -> None:
        """Test parameterized queries."""
        connected_db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE)")
        
        # Insert with parameters
        connected_db.execute(
            "INSERT INTO users (email) VALUES (?)",
            ("test@example.com",)
        )
        
        # Query with named parameters
        result = connected_db.fetchone(
            "SELECT * FROM users WHERE email = :email",
            {"email": "test@example.com"}
        )
        assert result is not None
        assert result["email"] == "test@example.com"

    def test_transaction_commit(self, connected_db: DatabaseConnection) -> None:
        """Test transaction commit."""
        connected_db.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, value TEXT)")
        
        with connected_db.transaction():
            connected_db.execute("INSERT INTO items (value) VALUES (?)", ("item1",))
        
        # Verify data was committed
        result = connected_db.fetchall("SELECT * FROM items")
        assert len(result) == 1

    def test_transaction_rollback_on_error(self, connected_db: DatabaseConnection) -> None:
        """Test transaction rollback on error."""
        connected_db.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, code TEXT UNIQUE)")
        
        # Insert first item
        connected_db.execute("INSERT INTO products (code) VALUES (?)", ("PROD001",))
        
        # Try to insert in transaction that will fail
        with pytest.raises(Exception):
            with connected_db.transaction():
                connected_db.execute("INSERT INTO products (code) VALUES (?)", ("PROD002",))
                # This will cause UNIQUE constraint violation
                connected_db.execute("INSERT INTO products (code) VALUES (?)", ("PROD002",))
        
        # Verify rollback - only first insert should exist
        result = connected_db.fetchall("SELECT * FROM products")
        assert len(result) == 1
        assert result[0]["code"] == "PROD001"

    def test_fetchone(self, connected_db: DatabaseConnection) -> None:
        """Test fetchone method."""
        connected_db.execute("CREATE TABLE single (id INTEGER PRIMARY KEY, val TEXT)")
        connected_db.execute("INSERT INTO single (val) VALUES (?), (?), (?)", ("a", "b", "c"))
        
        result = connected_db.fetchone("SELECT * FROM single ORDER BY id LIMIT 1")
        assert result is not None
        assert result["val"] == "a"

    def test_fetchmany(self, connected_db: DatabaseConnection) -> None:
        """Test fetchmany method."""
        connected_db.execute("CREATE TABLE multi (id INTEGER PRIMARY KEY, val TEXT)")
        connected_db.execute(
            "INSERT INTO multi (val) VALUES (?), (?), (?), (?), (?)",
            ("v1", "v2", "v3", "v4", "v5")
        )
        
        result = connected_db.fetchmany("SELECT * FROM multi ORDER BY id", size=3)
        assert len(result) == 3
        assert result[0]["val"] == "v1"
        assert result[2]["val"] == "v3"

    def test_get_table_count(self, connected_db: DatabaseConnection) -> None:
        """Test getting table count."""
        # Initially should be 0 (no user tables)
        assert connected_db.get_table_count() == 0
        
        # Create tables
        connected_db.execute("CREATE TABLE table1 (id INTEGER)")
        connected_db.execute("CREATE TABLE table2 (id INTEGER)")
        
        assert connected_db.get_table_count() == 2

    def test_context_manager(self, temp_db_path: Path) -> None:
        """Test using DatabaseConnection as context manager."""
        with DatabaseConnection(temp_db_path) as conn:
            assert conn.is_connected
            conn.execute("CREATE TABLE ctx_test (id INTEGER)")
        
        # Connection should be closed after context
        assert not conn.is_connected

    def test_nonexistent_database_file(self, temp_db_path: Path) -> None:
        """Test opening nonexistent database creates it."""
        # Delete the temp file if it exists
        if temp_db_path.exists():
            temp_db_path.unlink()
        
        conn = DatabaseConnection(temp_db_path)
        conn.connect()
        assert conn.is_connected
        assert temp_db_path.exists()
        conn.disconnect()

    def test_enable_disable_foreign_keys(self, connected_db: DatabaseConnection) -> None:
        """Test enabling and disabling foreign keys."""
        # Initially enabled by default
        assert connected_db.foreign_keys_enabled
        
        # Disable
        connected_db.disable_foreign_keys()
        assert not connected_db.foreign_keys_enabled
        
        # Enable again
        connected_db.enable_foreign_keys()
        assert connected_db.foreign_keys_enabled

    def test_rollback_method(self, connected_db: DatabaseConnection) -> None:
        """Test explicit rollback."""
        connected_db.execute("CREATE TABLE rollback_test (id INTEGER PRIMARY KEY, val TEXT)")
        connected_db.execute("INSERT INTO rollback_test (val) VALUES (?)", ("initial",))
        connected_db.commit()
        
        # Start new transaction
        connected_db.execute("INSERT INTO rollback_test (val) VALUES (?)", ("to_rollback",))
        connected_db.rollback()
        
        # Should only have initial row
        result = connected_db.fetchall("SELECT * FROM rollback_test")
        assert len(result) == 1
        assert result[0]["val"] == "initial"
