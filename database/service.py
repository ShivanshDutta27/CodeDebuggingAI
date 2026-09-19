"""Database Service for Fixie AI Debugger.

Provides high-level database operations:
- Schema initialization (database and tables creation)
- Session recording and retrieval
- Graceful health checking and diagnostic reporting
"""

import logging
from typing import Optional, List, Tuple
from database.config import DatabaseConfig, get_db_config
from database.connection import (
    get_connection,
    get_cursor,
    create_connection,
    test_connection,
    DatabaseConnectionError,
)
from database.models import (
    DebuggingSession,
    CREATE_DEBUGGING_SESSIONS_TABLE,
    SCHEMA_DEFINITIONS,
)

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service layer coordinating MySQL database operations."""

    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or get_db_config()

    def check_connection(self) -> Tuple[bool, str]:
        """Verify database connectivity and check if the schema is initialized."""
        is_connected, msg = test_connection(include_db=False, config=self.config)
        if not is_connected:
            return False, f"Server unreachable: {msg}"

        # Check if specific database exists
        try:
            with get_connection(include_db=False, config=self.config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s;",
                        (self.config.database,),
                    )
                    db_exists = cursor.fetchone() is not None

            if not db_exists:
                return True, f"{msg} (Note: Database '{self.config.database}' does not exist yet. Run init_db())"

            # Check if debugging_sessions table exists
            with get_connection(include_db=True, config=self.config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SHOW TABLES LIKE 'debugging_sessions';")
                    table_exists = cursor.fetchone() is not None

            table_status = "Table 'debugging_sessions' is ready." if table_exists else "Table 'debugging_sessions' not found. Run init_db()."
            return True, f"{msg} | Database '{self.config.database}' found. {table_status}"
        except Exception as e:
            return False, f"Error inspecting database: {e}"

    def init_db(self, create_database_if_missing: bool = True) -> bool:
        """Initialize database schema and tables.

        Creates the target database (if missing and permitted) and the
        `debugging_sessions` table if it does not exist.
        """
        try:
            # Step 1: Create database if missing
            if create_database_if_missing:
                with get_connection(include_db=False, config=self.config) as conn:
                    with conn.cursor() as cursor:
                        # Database names cannot use parameter substitution in DDL
                        safe_db_name = self.config.database.replace("`", "``")
                        cursor.execute(
                            f"CREATE DATABASE IF NOT EXISTS `{safe_db_name}` "
                            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                        )
                    conn.commit()

            # Step 2: Create required tables
            with get_connection(include_db=True, config=self.config) as conn:
                with conn.cursor() as cursor:
                    for table_name, ddl in SCHEMA_DEFINITIONS.items():
                        cursor.execute(ddl)
                conn.commit()

            logger.info("Database schema initialized successfully.")
            return True
        except Exception as e:
            logger.error("Failed to initialize database: %s", e)
            raise DatabaseConnectionError(f"Schema initialization failed: {e}") from e

    def create_session(
        self,
        original_code: str,
        language: str = "python",
        error_description: Optional[str] = None,
    ) -> Optional[DebuggingSession]:
        """Store a new debugging session record in MySQL.

        Returns:
            The created DebuggingSession model with assigned ID and created_at.
        """
        sql = """
        INSERT INTO debugging_sessions (language, original_code, error_description)
        VALUES (%s, %s, %s);
        """
        try:
            with get_cursor(include_db=True, config=self.config) as cursor:
                cursor.execute(sql, (language, original_code, error_description))
                session_id = cursor.lastrowid

            return self.get_session(session_id)
        except Exception as e:
            logger.error("Failed to save debugging session: %s", e)
            raise

    def get_session(self, session_id: int) -> Optional[DebuggingSession]:
        """Fetch a single debugging session by primary key ID."""
        sql = """
        SELECT id, language, original_code, error_description, created_at
        FROM debugging_sessions
        WHERE id = %s;
        """
        with get_cursor(include_db=True, config=self.config) as cursor:
            cursor.execute(sql, (session_id,))
            row = cursor.fetchone()
            if row:
                return DebuggingSession.from_row(row)
            return None

    def list_sessions(self, limit: int = 10, offset: int = 0) -> List[DebuggingSession]:
        """Retrieve recent debugging sessions ordered by created_at DESC."""
        sql = """
        SELECT id, language, original_code, error_description, created_at
        FROM debugging_sessions
        ORDER BY created_at DESC, id DESC
        LIMIT %s OFFSET %s;
        """
        with get_cursor(include_db=True, config=self.config) as cursor:
            cursor.execute(sql, (limit, offset))
            rows = cursor.fetchall()
            return [DebuggingSession.from_row(row) for row in rows]
