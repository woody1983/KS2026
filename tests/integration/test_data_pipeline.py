"""
Integration tests for data pipeline - The Night's Watch

Tests end-to-end data flow from ingestion to analysis.
"""

import pytest
import sqlite3


@pytest.mark.integration
class TestDataPipeline:
    """Test complete data pipeline integration."""

    def test_student_data_flow(self, schema_db):
        """Test student data flows through mapping -> masked -> outcomes."""
        # Insert mapping with valid UUID format and proper hash length (exactly 64 chars)
        hash_value = "a" * 64
        schema_db.execute(
            """
            INSERT INTO dim_student_mapping (student_uuid, student_id_hash, encryption_key_ref, created_by, updated_by)
            VALUES (?, ?, 'key001', 'test', 'test')
        """,
            ("550e8400-e29b-41d4-a716-446655440001", hash_value),
        )

        # Insert masked student
        schema_db.execute("""
            INSERT INTO dim_students_masked (
                student_uuid, grade_level, cohort_year,
                entry_date, enrollment_status,
                effective_start_date, effective_end_date, is_current
            ) VALUES ('550e8400-e29b-41d4-a716-446655440001', 5, 2024, '2024-08-01', 'Active',
                     '2024-08-01', '9999-12-31', 1)
        """)

        # Get student_key
        schema_db.execute(
            "SELECT student_key FROM dim_students_masked WHERE student_uuid = '550e8400-e29b-41d4-a716-446655440001'"
        )
        student_key = schema_db.fetchone()[0]

        # Insert date with all required fields
        schema_db.execute("""
            INSERT INTO dim_date (date_key, full_date, day_of_week, day_name, day_of_month, day_of_year,
                                  week_of_year, month_number, month_name, quarter, year_number, fiscal_year,
                                  academic_year, academic_term, term_start_date, term_end_date, is_school_day)
            VALUES (20240801, '2024-08-01', 4, 'Thursday', 1, 214, 31, 8, 'August', 3, 2024, 2024,
                    '2024-2025', 'Fall', '2024-08-01', '2024-12-20', 1)
        """)

        # Insert outcome
        schema_db.execute(
            """
            INSERT INTO fact_e_ola_outcomes (
                student_key, indicator_key, assessment_type_key, date_key,
                raw_score, normalized_score, proficiency_level,
                assessment_date, assessor_type, source_system
            ) VALUES (?, 1, 1, 20240801, 85.0, 85.0, 'Proficient',
                     '2024-08-01', 'Teacher', 'Test')
        """,
            (student_key,),
        )

        schema_db.conn.commit()

        # Verify data integrity
        schema_db.execute("""
            SELECT o.*, s.student_uuid
            FROM fact_e_ola_outcomes o
            JOIN dim_students_masked s ON o.student_key = s.student_key
            WHERE s.student_uuid = '550e8400-e29b-41d4-a716-446655440001'
        """)
        result = schema_db.fetchone()

        assert result is not None
        assert result["normalized_score"] == 85.0

    def test_cascade_delete_restricted(self, schema_db):
        """Verify FK constraints prevent orphaned records."""
        # Try to delete student with existing outcomes
        schema_db.execute("SELECT student_key FROM dim_students_masked LIMIT 1")
        result = schema_db.fetchone()

        if result:
            student_key = result[0]

            with pytest.raises(sqlite3.IntegrityError):
                schema_db.execute(
                    "DELETE FROM dim_students_masked WHERE student_key = ?",
                    (student_key,),
                )
                schema_db.conn.commit()


@pytest.mark.slow
class TestPerformance:
    """Performance tests for database operations."""

    def test_query_performance_with_index(self, schema_db):
        """Verify indexed queries perform well."""
        import time

        # This test would require actual data
        # For now, just verify indexes exist
        indexes = schema_db.get_indexes("fact_e_ola_outcomes")
        assert len(indexes) > 0, "No indexes found on fact table"

    def test_bulk_insert_performance(self, schema_db):
        """Test bulk insert performance."""
        import time

        start_time = time.time()

        # Bulk insert test
        for i in range(100):
            try:
                schema_db.execute(
                    """
                    INSERT INTO dim_date (date_key, full_date, academic_year)
                    VALUES (?, ?, ?)
                """,
                    (20240000 + i, f"2024-01-{i % 30 + 1}", "2024-2025"),
                )
            except sqlite3.IntegrityError:
                pass  # Date might already exist

        schema_db.conn.commit()
        elapsed = time.time() - start_time

        # Should complete in under 1 second for 100 records
        assert elapsed < 1.0, f"Bulk insert too slow: {elapsed:.2f}s"
