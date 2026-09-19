"""Database package for Fixie AI Debugger.

Exports core connection utilities, data models, and the high-level DatabaseService.
"""

from database.config import DatabaseConfig, get_db_config
from database.connection import (
    create_connection,
    get_connection,
    get_cursor,
    test_connection,
    DatabaseConnectionError,
)
from database.models import (
    DebuggingSession,
    CREATE_DEBUGGING_SESSIONS_TABLE,
    SCHEMA_DEFINITIONS,
)
from database.service import DatabaseService

__all__ = [
    "DatabaseConfig",
    "get_db_config",
    "create_connection",
    "get_connection",
    "get_cursor",
    "test_connection",
    "DatabaseConnectionError",
    "DebuggingSession",
    "CREATE_DEBUGGING_SESSIONS_TABLE",
    "SCHEMA_DEFINITIONS",
    "DatabaseService",
]
