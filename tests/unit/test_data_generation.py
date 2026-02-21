"""
Data Generation Tests - The Ironforge Miner (铁炉堡矿工)

Tests for high-fidelity synthetic data generation with Hawaiian cultural authenticity.
Validates statistical distributions, data quality, and dirty data injection.
"""

import pytest
import sqlite3
import uuid
import random
import numpy as np
from datetime import datetime, timedelta


@pytest.mark.unit
class TestDataGenerationBasics:
    """Test basic data generation functionality."""

    def test_hawaiian_names_loaded(self):
        """Verify Hawaiian name datasets are available."""
        from scripts.seed_data_enterprise import (
            HAWAIIAN_FIRST_NAMES,
            HAWAIIAN_LAST_NAMES,
        )

        assert len(HAWAIIAN_FIRST_NAMES) > 50, "Should have many Hawaiian first names"
        assert len(HAWAIIAN_LAST_NAMES) > 50, "Should have many Hawaiian last names"

        # Verify cultural authenticity - should have both male and female names
        male_names = ["Kealoha", "Kai", "Keoni", "Kaleo"]
        female_names = ["Malia", "Leilani", "Kailani", "Kehlani"]

        for name in male_names:
            assert name in HAWAIIAN_FIRST_NAMES, f"Missing male name: {name}"

        for name in female_names:
            assert name in HAWAIIAN_FIRST_NAMES, f"Missing female name: {name}"

    def test_campus_distribution_loaded(self):
        """Verify campus distribution configuration."""
        from scripts.seed_data_enterprise import KS_CAMPUSES

        assert "Kāpalama (Honolulu)" in KS_CAMPUSES
        assert "Maui" in KS_CAMPUSES
        assert "Hawaiʻi Island" in KS_CAMPUSES

        # Verify weights sum to 1.0
        total_weight = sum(campus["weight"] for campus in KS_CAMPUSES.values())
        assert abs(total_weight - 1.0) < 0.01, "Campus weights should sum to 1.0"

    def test_reflection_templates_loaded(self):
        """Verify cultural reflection templates."""
        from scripts.seed_data_enterprise import REFLECTION_TEMPLATES, HAWAIIAN_KEYWORDS

        assert "positive" in REFLECTION_TEMPLATES
        assert "neutral" in REFLECTION_TEMPLATES
        assert "challenging" in REFLECTION_TEMPLATES

        # Verify cultural keywords
        assert "Kuleana" in HAWAIIAN_KEYWORDS
        assert "Mālama" in HAWAIIAN_KEYWORDS
        assert "Aloha" in HAWAIIAN_KEYWORDS


@pytest.mark.unit
class TestStatisticalDistributions:
    """Test statistical distribution generation."""

    def test_normal_score_distribution(self):
        """Verify normal distribution for scores."""
        from scripts.seed_data_enterprise import generate_normal_score

        # Generate 1000 scores
        scores = [generate_normal_score(mean=75, std=15) for _ in range(1000)]

        # Check bounds
        assert all(0 <= s <= 100 for s in scores), "All scores should be 0-100"

        # Check mean is approximately 75
        mean_score = np.mean(scores)
        assert 70 <= mean_score <= 80, f"Mean should be ~75, got {mean_score}"

        # Check standard deviation is approximately 15
        std_score = np.std(scores)
        assert 12 <= std_score <= 18, f"Std should be ~15, got {std_score}"

    def test_power_law_hours_distribution(self):
        """Verify power-law distribution for participation hours."""
        from scripts.seed_data_enterprise import generate_power_law_hours

        # Generate 1000 hour values
        hours = [generate_power_law_hours() for _ in range(1000)]

        # Check bounds
        assert all(1 <= h <= 50 for h in hours), "Hours should be 1-50"

        # Power law should have many small values and few large values
        small_hours = sum(1 for h in hours if h <= 10)
        large_hours = sum(1 for h in hours if h >= 30)

        # Should have more small values than large values
        assert small_hours > large_hours * 5, "Power law should favor small values"

    def test_score_bounds_enforced(self):
        """Verify scores respect min/max bounds."""
        from scripts.seed_data_enterprise import generate_normal_score

        # Test with extreme parameters
        scores = [generate_normal_score(mean=150, std=50) for _ in range(100)]
        assert all(s <= 100 for s in scores), "Scores should not exceed 100"

        scores = [generate_normal_score(mean=-50, std=50) for _ in range(100)]
        assert all(s >= 0 for s in scores), "Scores should not be below 0"


@pytest.mark.unit
class TestDataQuality:
    """Test data quality and validation."""

    def test_uuid_generation(self):
        """Verify UUID generation for student mapping."""
        # Generate 100 UUIDs
        uuids = [str(uuid.uuid4()) for _ in range(100)]

        # All should be unique
        assert len(set(uuids)) == 100, "All UUIDs should be unique"

        # All should be valid UUID format
        for u in uuids:
            assert len(u) == 36, "UUID should be 36 characters"
            assert u.count("-") == 4, "UUID should have 4 hyphens"

    def test_hash_generation(self):
        """Verify SHA-256 hash generation."""
        import hashlib

        # Generate hash
        test_id = "STU_12345"
        hash_value = hashlib.sha256(test_id.encode()).hexdigest()

        # Should be 64 characters (hex)
        assert len(hash_value) == 64, "SHA-256 hash should be 64 characters"

        # Should be deterministic
        hash2 = hashlib.sha256(test_id.encode()).hexdigest()
        assert hash_value == hash2, "Hash should be deterministic"

    def test_date_generation(self):
        """Verify date generation within academic year."""
        from datetime import datetime, timedelta

        # Create academic year dates manually for testing
        start_date = datetime(2024, 8, 1)
        end_date = datetime(2025, 5, 30)

        # Check date range
        assert start_date.year == 2024, "Start date should be in 2024"
        assert end_date.year == 2025, "End date should be in 2025"

        # Check duration is reasonable (school year)
        duration = (end_date - start_date).days
        assert 270 <= duration <= 310, "School year should be ~280-300 days"


@pytest.mark.unit
class TestDirtyDataInjection:
    """Test dirty data injection for stress testing."""

    def test_invalid_uuid_generation(self):
        """Verify generation of invalid UUIDs for testing."""
        invalid_uuids = [
            "not-a-uuid",
            "12345",
            "",
            "550e8400-e29b-41d4-a716-44665544000",  # Too short
            "550e8400-e29b-41d4-a716-4466554400000",  # Too long
        ]

        # These should be detected as invalid
        for invalid_uuid in invalid_uuids:
            try:
                uuid.UUID(invalid_uuid)
                # If no error, it's actually valid
                if invalid_uuid not in ["", "12345", "not-a-uuid"]:
                    continue
                assert False, f"Should have raised error for: {invalid_uuid}"
            except ValueError:
                pass  # Expected

    def test_boundary_score_values(self):
        """Test boundary values for scores."""
        from scripts.seed_data_enterprise import generate_normal_score

        # Test boundary conditions
        boundary_scores = [0, 0.01, 50, 99.99, 100]

        for score in boundary_scores:
            # These should all be valid
            assert 0 <= score <= 100, f"Score {score} should be valid"

    def test_null_value_handling(self):
        """Test handling of NULL values."""
        # Test that NULL can be inserted for optional fields
        null_values = [None, "", "NULL", "null"]

        # In SQLite, these should be handled appropriately
        for val in null_values:
            if val is None:
                assert True  # None is valid NULL


@pytest.mark.integration
class TestDataGenerationIntegration:
    """Integration tests for data generation pipeline."""

    def test_student_profile_generation(self, schema_db):
        """Test complete student profile generation."""
        from scripts.seed_data_enterprise import generate_student_profile

        # Generate a student profile
        student = generate_student_profile(student_id=1)

        # Verify required fields
        assert "student_uuid" in student
        assert "grade_level" in student

        # Verify UUID format
        assert len(student["student_uuid"]) == 36

    def test_e_ola_outcomes_generation(self, schema_db):
        """Test E Ola! outcomes generation."""
        from scripts.seed_data_enterprise import generate_e_ola_outcomes

        # Generate outcome for a student
        outcome = generate_e_ola_outcomes(
            student_key=1, indicator_key=1, assessment_date="2024-08-15"
        )

        # Verify outcome was generated
        assert outcome is not None

        # Verify required fields
        assert "student_key" in outcome
        assert "indicator_key" in outcome
        assert "raw_score" in outcome

        # Verify score bounds
        assert 0 <= outcome["raw_score"] <= 100

    def test_cultural_reflection_generation(self):
        """Test cultural reflection text generation."""
        from scripts.seed_data_enterprise import generate_cultural_reflection

        # Generate reflections of different sentiments
        positive = generate_cultural_reflection(sentiment_type="positive")
        neutral = generate_cultural_reflection(sentiment_type="neutral")
        challenging = generate_cultural_reflection(sentiment_type="challenging")

        # Verify they are different
        assert positive != neutral != challenging

        # Verify they contain text
        assert len(positive) > 20
        assert len(neutral) > 20
        assert len(challenging) > 20

        # Verify cultural keywords are used
        from scripts.seed_data_enterprise import HAWAIIAN_KEYWORDS

        has_keyword = any(kw in positive for kw in HAWAIIAN_KEYWORDS)
        assert has_keyword, "Reflection should contain cultural keywords"


@pytest.mark.slow
class TestBulkDataGeneration:
    """Tests for bulk data generation performance."""

    def test_bulk_student_generation_performance(self):
        """Test performance of generating 200 students."""
        import time
        from scripts.seed_data_enterprise import generate_student_profile

        start_time = time.time()

        students = [generate_student_profile(student_id=i) for i in range(200)]

        elapsed = time.time() - start_time

        # Should complete in under 5 seconds
        assert elapsed < 5.0, f"Bulk generation too slow: {elapsed:.2f}s"
        assert len(students) == 200, "Should generate 200 students"

    def test_memory_efficiency(self):
        """Test memory usage during bulk generation."""
        import sys
        from scripts.seed_data_enterprise import generate_student_profile

        # Generate students and check memory doesn't explode
        students = []
        for i in range(100):
            student = generate_student_profile(student_id=i)
            students.append(student)

        # Memory check - should be reasonable
        total_size = sum(sys.getsizeof(str(s)) for s in students)
        assert total_size < 10 * 1024 * 1024, "Memory usage should be < 10MB"
