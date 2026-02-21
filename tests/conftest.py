"""
Database testing configuration and fixtures for E Ola! Learner Analytics System.

The Night's Watch - Database Architecture & Security
Ensures database integrity, constraint validation, and DDM compliance.
"""

import pytest
import sqlite3
import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
SCHEMA_DIR = PROJECT_ROOT / "schema"


class DatabaseTestHelper:
    """Helper class for database testing operations."""

    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        # Enable foreign key constraints
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        return self

    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_script(self, script_path):
        """Execute SQL script from file."""
        with open(script_path, "r") as f:
            self.cursor.executescript(f.read())
        self.conn.commit()

    def execute(self, sql, params=None):
        """Execute SQL with optional parameters."""
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        return self.cursor

    def fetchall(self):
        """Fetch all results."""
        return self.cursor.fetchall()

    def fetchone(self):
        """Fetch single result."""
        return self.cursor.fetchone()

    def get_table_names(self):
        """Get all table names in database."""
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return [row[0] for row in self.cursor.fetchall()]

    def get_view_names(self):
        """Get all view names in database."""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        return [row[0] for row in self.cursor.fetchall()]

    def get_table_schema(self, table_name):
        """Get CREATE TABLE statement."""
        self.cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_foreign_keys(self, table_name):
        """Get foreign key constraints for table."""
        self.cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        return self.cursor.fetchall()

    def get_indexes(self, table_name):
        """Get indexes for table."""
        self.cursor.execute(f"PRAGMA index_list({table_name})")
        return self.cursor.fetchall()

    def check_constraint_exists(self, table_name, constraint_name):
        """Check if a named constraint exists."""
        schema = self.get_table_schema(table_name)
        return constraint_name.lower() in schema.lower() if schema else False

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


@pytest.fixture(scope="session")
def db_helper():
    """Session-scoped database helper."""
    return DatabaseTestHelper


@pytest.fixture
def fresh_db():
    """Fresh in-memory database for each test."""
    helper = DatabaseTestHelper(":memory:").connect()
    yield helper
    helper.close()


@pytest.fixture
def schema_db(fresh_db):
    """Database with schema loaded."""
    schema_path = SCHEMA_DIR / "v1_1_enterprise_schema.sql"
    if schema_path.exists():
        fresh_db.execute_script(schema_path)
    yield fresh_db


@pytest.fixture
def sample_student_data():
    """Sample student data for testing."""
    return {
        "student_key": 1,
        "student_uuid": "550e8400-e29b-41d4-a716-446655440000",
        "grade_level": 5,
        "campus_code": "KAP",
        "entry_date": "2024-08-01",
        "current_status": "Active",
        "is_hoku_scholar": 0,
    }


@pytest.fixture
def sample_outcome_data():
    """Sample outcome data for testing."""
    return {
        "student_key": 1,
        "indicator_key": 1,
        "assessment_type_key": 1,
        "date_key": 20240801,
        "raw_score": 85.5,
        "normalized_score": 85.5,
        "proficiency_level": "Proficient",
        "assessment_date": "2024-08-15",
        "assessor_type": "Teacher",
        "source_system": "Test",
    }


@pytest.fixture
def invalid_outcome_data():
    """Invalid outcome data for constraint testing."""
    return {
        "student_key": 99999,  # Non-existent student
        "indicator_key": 1,
        "assessment_type_key": 1,
        "date_key": 20240801,
        "raw_score": 150.0,  # Invalid: > 100
        "normalized_score": 150.0,
        "proficiency_level": "InvalidLevel",
        "assessment_date": "2024-08-15",
        "assessor_type": "Teacher",
        "source_system": "Test",
    }


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "ddm: DDM tests")
    config.addinivalue_line("markers", "schema: Schema tests")
