# SQLite Database Manager

A professional desktop application for managing SQLite databases with a modern graphical interface.

## Description

SQLite Database Manager is a comprehensive tool for creating, opening, viewing, managing, editing, and maintaining SQLite databases visually without using command line tools. Built with Python and PySide6, it provides an intuitive interface for database operations while maintaining performance and security.

## Features

### Core Features
- **Database Management**: Create, open, close, and manage multiple SQLite databases
- **Database Explorer**: Navigate tables, views, indexes, and triggers in a sidebar
- **Data Browser**: View and edit table data with pagination, sorting, and filtering
- **SQL Editor**: Execute custom SQL queries with syntax highlighting and history
- **Table Designer**: Create and modify table structures visually
- **Import/Export**: Import CSV files and export data to CSV, JSON, or SQL formats

### Advanced Features
- **Search**: Search across all tables for specific text values
- **Backup & Restore**: Safe database backup using SQLite API
- **Maintenance**: Vacuum, analyze, and integrity check operations
- **Query History**: Track and reuse previously executed queries
- **Dark Mode**: Light and dark theme support
- **Foreign Key Support**: View and manage foreign key relationships

### Security & Performance
- Parameterized queries to prevent SQL injection
- Transaction management with commit/rollback
- Efficient pagination for large datasets
- Async operations to prevent UI freezing
- Comprehensive error handling and logging

## Requirements

- Python 3.12 or later (compatible with 3.8+)
- PySide6
- pytest (for running tests)

## Installation

### 1. Clone or download the project

```bash
cd sqlite_manager
```

### 2. Create virtual environment (recommended)

```bash
python -m venv venv
```

### 3. Activate virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### Development Mode

```bash
python main.py
```

### With Logging Level

```bash
python main.py --log-level DEBUG
```

## Building Windows EXE

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Build the executable

```bash
pyinstaller --onefile --windowed --name "SQLite Database Manager" --icon=resources/icon.ico main.py
```

Or use the provided spec file:

```bash
pyinstaller sqlite_manager.spec
```

The executable will be created in the `dist` directory.

## Project Structure

```
sqlite_manager/
│
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
│
├── app/                   # Application core
│   ├── __init__.py
│   ├── application.py     # Main application class
│   └── settings.py        # Application settings
│
├── core/                  # Core utilities
│   ├── __init__.py
│   ├── config.py          # Configuration constants
│   └── exceptions.py      # Custom exceptions
│
├── database/              # Database layer
│   ├── __init__.py
│   ├── connection.py      # Connection management
│   ├── manager.py         # Database operations
│   └── schema.py          # Schema information
│
├── models/                # Data models
│   ├── __init__.py
│   └── table_model.py     # Qt table models
│
├── repositories/          # Data access layer
│   ├── __init__.py
│   ├── base_repository.py
│   └── table_repository.py
│
├── services/              # Business logic
│   ├── __init__.py
│   ├── import_service.py
│   ├── export_service.py
│   ├── search_service.py
│   └── query_history.py
│
├── ui/                    # User interface
│   ├── __init__.py
│   ├── main_window.py     # Main window
│   ├── explorer/          # Database explorer
│   ├── browser/           # Data browser
│   ├── structure/         # Table structure
│   ├── editor/            # SQL editor
│   ├── dialogs/           # Dialog windows
│   └── widgets/           # Reusable widgets
│
├── utils/                 # Utilities
│   ├── __init__.py
│   ├── logger.py          # Logging setup
│   └── validators.py      # Input validation
│
├── styles/                # Stylesheets
│   ├── __init__.py
│   ├── light_theme.qss
│   └── dark_theme.qss
│
└── tests/                 # Unit tests
    ├── __init__.py
    ├── test_database/
    ├── test_repositories/
    └── test_services/
```

## Running Tests

### Run all tests

```bash
pytest tests/ -v
```

### Run specific test module

```bash
pytest tests/test_database/ -v
```

### Run with coverage

```bash
pytest tests/ --cov=sqlite_manager --cov-report=html
```

## Troubleshooting

### Common Issues

**1. PySide6 not found**
```bash
pip install pyside6
```

**2. Database locked error**
- Close any other applications using the database
- Ensure proper transaction management (commit/rollback)

**3. UI freezing on large queries**
- Use pagination in data browser
- Add LIMIT clause to SQL queries
- Heavy operations run in separate threads

**4. Import errors**
- Ensure you're in the project root directory
- Check that all dependencies are installed
- Verify Python version (3.12+)

### Logging

Logs are stored in the application directory. To view debug information:

```bash
python main.py --log-level DEBUG
```

Log files can be found in the `logs` directory.

## License

This project is provided as-is for educational and practical use.

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Use PEP 8 style guide
2. Add type hints to functions and classes
3. Write docstrings for public methods
4. Add tests for new features
5. Update documentation as needed

## Version History

- **1.0.0** - Initial release with core features
  - Database management
  - Data browsing and editing
  - SQL editor
  - Import/Export
  - Dark mode support
