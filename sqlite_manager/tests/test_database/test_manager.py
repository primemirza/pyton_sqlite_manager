"""
Unit tests for database manager module.
"""

import pytest
from pathlib import Path
import tempfile
import os

from database.manager import DatabaseManager
from core.exceptions import DatabaseConnectionError, BackupError, RestoreError


class TestDatabaseManager:
    """Test cases for DatabaseManager class."""

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
    def db_manager(self, temp_db_path: Path) -> DatabaseManager:
        """Create a DatabaseManager with open database."""
        manager = DatabaseManager()
        manager.create_database(temp_db_path)
        yield manager
        manager.close_database()
        if temp_db_path.exists():
            temp_db_path.unlink()

    def test_create_database(self, temp_db_path: Path) -> None:
        """Test database creation."""
        if temp_db_path.exists():
            temp_db_path.unlink()
        
        manager = DatabaseManager()
        manager.create_database(temp_db_path)
        
        assert manager.is_connected
        assert manager.db_path == temp_db_path
        assert temp_db_path.exists()
        
        manager.close_database()

    def test_open_database(self, temp_db_path: Path) -> None:
        """Test opening existing database."""
        # Create database first
        manager1 = DatabaseManager()
        manager1.create_database(temp_db_path)
        manager1.close_database()
        
        # Open it again
        manager2 = DatabaseManager()
        manager2.open_database(temp_db_path)
        
        assert manager2.is_connected
        assert manager2.db_path == temp_db_path
        
        manager2.close_database()

    def test_open_nonexistent_database_raises_error(self, temp_db_path: Path) -> None:
        """Test that opening nonexistent database raises error."""
        if temp_db_path.exists():
            temp_db_path.unlink()
        
        manager = DatabaseManager()
        with pytest.raises(DatabaseConnectionError):
            manager.open_database(temp_db_path)

    def test_get_sqlite_version(self, db_manager: DatabaseManager) -> None:
        """Test getting SQLite version."""
        version = db_manager.get_sqlite_version()
        assert version is not None
        assert len(version) > 0
        # Version should be in format like "3.x.y"
        assert version.count(".") >= 1

    def test_get_database_info(self, db_manager: DatabaseManager) -> None:
        """Test getting database information."""
        info = db_manager.get_database_info()
        
        assert "path" in info
        assert "size" in info
        assert "sqlite_version" in info
        assert "table_count" in info
        assert "view_count" in info
        assert "index_count" in info
        assert "trigger_count" in info
        
        assert info["table_count"] == 0  # No tables yet

    def test_get_tables(self, db_manager: DatabaseManager) -> None:
        """Test getting list of tables."""
        # Initially empty
        tables = db_manager.get_tables()
        assert len(tables) == 0
        
        # Create tables
        db_manager.connection.execute("CREATE TABLE users (id INTEGER)")
        db_manager.connection.execute("CREATE TABLE products (id INTEGER)")
        
        tables = db_manager.get_tables()
        assert len(tables) == 2
        assert "users" in tables
        assert "products" in tables

    def test_table_exists(self, db_manager: DatabaseManager) -> None:
        """Test checking if table exists."""
        assert not db_manager.table_exists("nonexistent")
        
        db_manager.connection.execute("CREATE TABLE test_table (id INTEGER)")
        assert db_manager.table_exists("test_table")
        assert not db_manager.table_exists("other_table")

    def test_get_table_info(self, db_manager: DatabaseManager) -> None:
        """Test getting table column information."""
        db_manager.connection.execute("""
            CREATE TABLE test_info (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                age INTEGER DEFAULT 0
            )
        """)
        
        columns = db_manager.get_table_info("test_info")
        assert len(columns) == 4
        
        # Check id column
        id_col = next(c for c in columns if c["name"] == "id")
        assert id_col["pk"] is True
        assert id_col["type"] == "INTEGER"
        
        # Check name column
        name_col = next(c for c in columns if c["name"] == "name")
        assert name_col["notnull"] is True
        
        # Check email column
        email_col = next(c for c in columns if c["name"] == "email")
        assert email_col["type"] == "TEXT"

    def test_get_foreign_keys(self, db_manager: DatabaseManager) -> None:
        """Test getting foreign key information."""
        db_manager.connection.execute("""
            CREATE TABLE parent (
                id INTEGER PRIMARY KEY
            )
        """)
        
        db_manager.connection.execute("""
            CREATE TABLE child (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER,
                FOREIGN KEY (parent_id) REFERENCES parent(id)
            )
        """)
        
        fks = db_manager.get_foreign_keys("child")
        assert len(fks) == 1
        assert fks[0]["table"] == "parent"
        assert fks[0]["from"] == "parent_id"
        assert fks[0]["to"] == "id"

    def test_get_views(self, db_manager: DatabaseManager) -> None:
        """Test getting view information."""
        db_manager.connection.execute("CREATE TABLE v_test (id INTEGER, val TEXT)")
        db_manager.connection.execute("""
            CREATE VIEW v_test_view AS
            SELECT id FROM v_test WHERE id > 0
        """)
        
        views = db_manager.get_views()
        assert len(views) == 1
        assert views[0]["name"] == "v_test_view"
        assert "SELECT" in views[0]["sql"]

    def test_get_triggers(self, db_manager: DatabaseManager) -> None:
        """Test getting trigger information."""
        db_manager.connection.execute("CREATE TABLE t_test (id INTEGER, val TEXT)")
        db_manager.connection.execute("""
            CREATE TRIGGER t_test_trigger
            AFTER INSERT ON t_test
            BEGIN
                UPDATE t_test SET val = 'updated' WHERE id = NEW.id;
            END
        """)
        
        triggers = db_manager.get_triggers()
        assert len(triggers) == 1
        assert triggers[0]["name"] == "t_test_trigger"
        assert triggers[0]["table"] == "t_test"

    def test_get_all_indexes(self, db_manager: DatabaseManager) -> None:
        """Test getting all indexes."""
        db_manager.connection.execute("CREATE TABLE idx_test (id INTEGER, val TEXT)")
        db_manager.connection.execute("CREATE INDEX idx_val ON idx_test(val)")
        
        indexes = db_manager.get_all_indexes()
        assert len(indexes) == 1
        assert indexes[0]["name"] == "idx_val"
        assert indexes[0]["table"] == "idx_test"

    def test_backup_database(self, db_manager: DatabaseManager, temp_db_path: Path) -> None:
        """Test database backup."""
        # Add some data
        db_manager.connection.execute("CREATE TABLE backup_test (id INTEGER)")
        db_manager.connection.execute("INSERT INTO backup_test VALUES (1), (2), (3)")
        db_manager.connection.commit()
        
        # Create backup
        backup_path = temp_db_path.parent / "backup_test.backup"
        db_manager.backup_database(backup_path)
        
        assert backup_path.exists()
        
        # Verify backup has data
        backup_manager = DatabaseManager()
        backup_manager.open_database(backup_path)
        count = backup_manager.connection.fetchone("SELECT COUNT(*) FROM backup_test")[0]
        assert count == 3
        backup_manager.close_database()
        
        # Cleanup
        backup_path.unlink()

    def test_vacuum_database(self, db_manager: DatabaseManager) -> None:
        """Test vacuum operation."""
        db_manager.connection.execute("CREATE TABLE vacuum_test (id INTEGER, data TEXT)")
        for i in range(100):
            db_manager.connection.execute(
                "INSERT INTO vacuum_test (data) VALUES (?)",
                ("x" * 1000,)
            )
        db_manager.connection.execute("DELETE FROM vacuum_test")
        db_manager.connection.commit()
        
        # Vacuum should complete without error
        db_manager.vacuum_database()

    def test_analyze_database(self, db_manager: DatabaseManager) -> None:
        """Test analyze operation."""
        db_manager.connection.execute("CREATE TABLE analyze_test (id INTEGER, val TEXT)")
        db_manager.connection.execute("CREATE INDEX idx_analyze ON analyze_test(val)")
        
        # Analyze should complete without error
        db_manager.analyze_database()

    def test_integrity_check_ok(self, db_manager: DatabaseManager) -> None:
        """Test integrity check on healthy database."""
        db_manager.connection.execute("CREATE TABLE integrity_test (id INTEGER)")
        db_manager.connection.commit()
        
        issues = db_manager.integrity_check()
        assert len(issues) == 0  # Should be empty for healthy database

    def test_close_database(self, temp_db_path: Path) -> None:
        """Test closing database."""
        manager = DatabaseManager()
        manager.create_database(temp_db_path)
        assert manager.is_connected
        
        manager.close_database()
        assert not manager.is_connected
