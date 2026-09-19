"""Database connection management for MySQL.

Provides robust connection handling, context managers, and health check diagnostics.
"""

from contextlib import contextmanager
from typing import Generator, Optional, Tuple, Any
import pymysql
import pymysql.cursors

from database.config import DatabaseConfig, get_db_config


class DatabaseConnectionError(Exception):
    """Custom exception raised when connection to MySQL fails."""
    pass


def create_connection(
    include_db: bool = True,
    config: Optional[DatabaseConfig] = None
) -> pymysql.Connection:
    """Create and return a new pymysql Connection instance.

    Args:
        include_db: Whether to select the configured database name on connect.
                    Set to False when connecting to the server to create the database.
        config: Optional DatabaseConfig. If omitted, uses environment configuration.
    """
    cfg = config or get_db_config()
    kwargs = cfg.to_pymysql_kwargs(include_db=include_db)
    kwargs["cursorclass"] = pymysql.cursors.DictCursor
    kwargs["autocommit"] = False

    try:
        return pymysql.connect(**kwargs)
    except pymysql.MySQLError as e:
        raise DatabaseConnectionError(
            f"Failed to connect to MySQL ({cfg.host}:{cfg.port}): {e}"
        ) from e


@contextmanager
def get_connection(
    include_db: bool = True,
    config: Optional[DatabaseConfig] = None
) -> Generator[pymysql.Connection, None, None]:
    """Context manager for obtaining a database connection with auto-closing."""
    conn = create_connection(include_db=include_db, config=config)
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass


@contextmanager
def get_cursor(
    include_db: bool = True,
    config: Optional[DatabaseConfig] = None
) -> Generator[pymysql.cursors.DictCursor, None, None]:
    """Context manager providing a transactional cursor.

    Commits on successful block execution, rollbacks on exception.
    """
    with get_connection(include_db=include_db, config=config) as conn:
        with conn.cursor() as cursor:
            try:
                yield cursor
                conn.commit()
            except Exception:
                conn.rollback()
                raise


def test_connection(
    include_db: bool = False,
    config: Optional[DatabaseConfig] = None
) -> Tuple[bool, str]:
    """Perform a diagnostic health check on the MySQL connection.

    Returns:
        (True, "Connected to MySQL <version>") if successful.
        (False, "<error message>") if connection fails.
    """
    try:
        with get_connection(include_db=include_db, config=config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT VERSION() AS version, CURRENT_USER() AS user;")
                row = cursor.fetchone()
                version = row.get("version", "unknown") if row else "unknown"
                user = row.get("user", "unknown") if row else "unknown"
                return True, f"Successfully connected as '{user}' to MySQL server (version: {version})"
    except Exception as e:
        return False, str(e)
