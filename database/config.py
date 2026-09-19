"""Database configuration module for Fixie AI Debugger.

Loads database connection settings from environment variables with safe defaults.
"""

import os
from dataclasses import dataclass
from typing import Any, Dict
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


@dataclass
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "3306"))
    user: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD", "")
    database: str = os.getenv("DB_NAME", "fixie_debugger")
    connect_timeout: int = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))
    charset: str = "utf8mb4"

    def to_pymysql_kwargs(self, include_db: bool = True) -> Dict[str, Any]:
        """Convert configuration to parameters accepted by pymysql.connect."""
        kwargs: Dict[str, Any] = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "connect_timeout": self.connect_timeout,
            "charset": self.charset,
        }
        if include_db and self.database:
            kwargs["database"] = self.database
        return kwargs

    def is_configured(self) -> bool:
        """Check if minimum required database configurations are present."""
        return bool(self.host and self.user and self.database)


def get_db_config() -> DatabaseConfig:
    """Return a new DatabaseConfig instance populated from current environment."""
    return DatabaseConfig()
