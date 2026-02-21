"""
Database Schema Tests - The Night's Watch

Validates database structure, tables, views, and schema integrity.
Ensures the Star Schema is correctly implemented.
"""

import pytest
from pathlib import Path


@pytest.mark.schema
class TestDatabaseSchema:
    """Test suite for database schema validation."""

    EXPECTED_TABLES = [
        # Dimension Tables
        "dim_student_mapping",
        "dim_students_masked",
        "dim_date",
        "dim_e_ola_indicators",
        "dim_assessment_types",
        "dim_pbl_projects",
        "dim_wellbeing_dimensions",
        # Fact Tables
        "fact_e_ola_outcomes",
        "fact_wellbeing_measurements",
        "fact_pbl_implementation",
        "fact_interventions",
        # Configuration Tables
        "cfg_indicator_weights",
        "cfg_ui_themes",
        # Audit Tables
        "sys_access_logs",
        "sys_change_logs",
    ]

    EXPECTED_VIEWS = [
        "vw_leader_cohort_summary",
        "vw_researcher_anonymized",
        "vw_teacher_student_outcomes",
        "vw_student_history",
    ]

    def test_schema_file_exists(self):
        """Verify schema SQL file exists."""
        schema_path = (
            Path(__file__).parent.parent.parent
            / "schema"
            / "v1_1_enterprise_schema.sql"
        )
        assert schema_path.exists(), f"Schema file not found: {schema_path}"

    def test_all_expected_tables_exist(self, schema_db):
        """Verify all expected tables are created."""
        tables = schema_db.get_table_names()

        for expected_table in self.EXPECTED_TABLES:
            assert expected_table in tables, f"Missing table: {expected_table}"

    def test_no_unexpected_tables(self, schema_db):
        """Verify no unexpected tables exist."""
        tables = set(schema_db.get_table_names())
        expected = set(self.EXPECTED_TABLES)

        unexpected = tables - expected
        assert not unexpected, f"Unexpected tables found: {unexpected}"

    def test_all_expected_views_exist(self, schema_db):
        """Verify all expected views are created."""
        views = schema_db.get_view_names()

        for expected_view in self.EXPECTED_VIEWS:
            assert expected_view in views, f"Missing view: {expected_view}"

    def test_student_mapping_table_structure(self, schema_db):
        """Verify dim_student_mapping has correct columns."""
        schema_db.execute("PRAGMA table_info(dim_student_mapping)")
        columns = {row[1] for row in schema_db.fetchall()}

        required_columns = {
            "mapping_id",
            "student_uuid",
            "student_id_hash",
            "created_at",
            "updated_at",
        }

        for col in required_columns:
            assert col in columns, f"Missing column in dim_student_mapping: {col}"

    def test_students_masked_scd2_support(self, schema_db):
        """Verify dim_students_masked supports SCD Type 2."""
        schema_db.execute("PRAGMA table_info(dim_students_masked)")
        columns = {row[1] for row in schema_db.fetchall()}

        scd2_columns = {
            "effective_start_date",
            "effective_end_date",
            "is_current",
            "previous_version_key",
        }

        for col in scd2_columns:
            assert col in columns, f"Missing SCD2 column: {col}"

    def test_audit_fields_on_all_tables(self, schema_db):
        """Verify all tables have created_at and updated_at."""
        tables = schema_db.get_table_names()

        # Skip audit tables themselves
        tables_to_check = [t for t in tables if not t.startswith("sys_")]

        for table in tables_to_check:
            schema_db.execute(f"PRAGMA table_info({table})")
            columns = {row[1] for row in schema_db.fetchall()}

            assert "created_at" in columns, f"Table {table} missing created_at"
            assert "updated_at" in columns, f"Table {table} missing updated_at"

    def test_e_ola_indicators_count(self, schema_db):
        """Verify exactly 14 E Ola! indicators exist."""
        schema_db.execute("SELECT COUNT(*) FROM dim_e_ola_indicators")
        count = schema_db.fetchone()[0]

        assert count == 14, f"Expected 14 indicators, found {count}"

    def test_indicator_categories(self, schema_db):
        """Verify indicators are categorized correctly."""
        schema_db.execute("""
            SELECT tier_level, COUNT(*) 
            FROM dim_e_ola_indicators 
            GROUP BY tier_level
        """)
        categories = {row[0]: row[1] for row in schema_db.fetchall()}

        assert categories.get("Roots") == 3, "Should have 3 Root indicators"
        assert categories.get("Trunk_Branches") == 3, (
            "Should have 3 Trunk/Branch indicators"
        )
        assert categories.get("Leaves") == 7, "Should have 7 Leaf indicators"
        assert categories.get("Fruits") == 1, "Should have 1 Fruit indicator"


@pytest.mark.schema
class TestForeignKeyConstraints:
    """Test suite for foreign key constraint validation."""

    def test_fact_outcomes_student_fk(self, schema_db):
        """Verify fact_e_ola_outcomes has FK to dim_students_masked."""
        fks = schema_db.get_foreign_keys("fact_e_ola_outcomes")
        fk_targets = {(fk[2], fk[3]) for fk in fks}  # (table, from_col)

        assert ("dim_students_masked", "student_key") in fk_targets

    def test_fact_outcomes_indicator_fk(self, schema_db):
        """Verify fact_e_ola_outcomes has FK to dim_e_ola_indicators."""
        fks = schema_db.get_foreign_keys("fact_e_ola_outcomes")
        fk_targets = {(fk[2], fk[3]) for fk in fks}

        assert ("dim_e_ola_indicators", "indicator_key") in fk_targets

    def test_fact_outcomes_date_fk(self, schema_db):
        """Verify fact_e_ola_outcomes has FK to dim_date."""
        fks = schema_db.get_foreign_keys("fact_e_ola_outcomes")
        fk_targets = {(fk[2], fk[3]) for fk in fks}

        assert ("dim_date", "date_key") in fk_targets

    def test_fact_outcomes_assessment_fk(self, schema_db):
        """Verify fact_e_ola_outcomes has FK to dim_assessment_types."""
        fks = schema_db.get_foreign_keys("fact_e_ola_outcomes")
        fk_targets = {(fk[2], fk[3]) for fk in fks}

        assert ("dim_assessment_types", "assessment_type_key") in fk_targets


@pytest.mark.schema
class TestIndexCreation:
    """Test suite for index validation."""

    def test_outcomes_student_date_index(self, schema_db):
        """Verify student+date composite index exists."""
        indexes = schema_db.get_indexes("fact_e_ola_outcomes")
        index_names = {idx[1] for idx in indexes}

        assert "idx_outcomes_student_date" in index_names

    def test_outcomes_indicator_date_index(self, schema_db):
        """Verify indicator+date composite index exists."""
        indexes = schema_db.get_indexes("fact_e_ola_outcomes")
        index_names = {idx[1] for idx in indexes}

        assert "idx_outcomes_indicator_date" in index_names

    def test_outcomes_proficiency_index(self, schema_db):
        """Verify proficiency level index exists."""
        indexes = schema_db.get_indexes("fact_e_ola_outcomes")
        index_names = {idx[1] for idx in indexes}

        assert "idx_outcomes_proficiency" in index_names
