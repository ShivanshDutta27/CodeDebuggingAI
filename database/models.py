"""Database models and schema definitions for Fixie AI Debugger.

Defines schemas and data classes for debugging sessions and modular extensions
for agent analyses, candidate patches, and validation records in future stages.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class DebuggingSession:
    """Represents a debugging session record in MySQL."""
    original_code: str
    language: str = "python"
    error_description: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert session model to dictionary."""
        d = asdict(self)
        if isinstance(self.created_at, datetime):
            d["created_at"] = self.created_at.isoformat()
        return d

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "DebuggingSession":
        """Construct a DebuggingSession instance from a MySQL row dictionary."""
        return cls(
            id=row.get("id"),
            language=row.get("language", "python"),
            original_code=row.get("original_code", ""),
            error_description=row.get("error_description"),
            created_at=row.get("created_at"),
        )


# SQL DDL for Stage 1: Debugging Sessions Table
CREATE_DEBUGGING_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS debugging_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    language VARCHAR(50) NOT NULL DEFAULT 'python',
    original_code LONGTEXT NOT NULL,
    error_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_language (language),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# Modular Extension Points for Upcoming Stages:
# ----------------------------------------------------
# Stage 2+: Agent Analyses (Syntax, Logic, Fixer records)
# Stage 3+: Candidate Patches & Fix Verification
# Stage 4+: Validation Results & Test Suite Runs
# Stage 5+: Memory Embeddings & Retrieval History
#
# These DDL statements can be loaded incrementally as features are enabled.
SCHEMA_DEFINITIONS = {
    "debugging_sessions": CREATE_DEBUGGING_SESSIONS_TABLE,
}
