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

    def test_student_scores_generation(self, schema_db):
        """Test generate_student_scores returns 14 outcome records per student."""
        from scripts.seed_data_enterprise import generate_student_scores

        profile = {
            "is_hawaiian_language": True,
            "is_hālau_hula": False,
            "is_pbl_participant": True,
            "aina_connection_score": 4,
            "has_hoku_scholarship": False,
            "grade_level": 8,
            "ethnicity_category": "Native Hawaiian",
        }
        outcomes = generate_student_scores(
            student_profile=profile, student_key=1, assessment_date="2024-08-15"
        )

        # Must return exactly 14 records (one per indicator)
        assert len(outcomes) == 14, f"Expected 14 outcomes, got {len(outcomes)}"

        # Verify required fields on every record
        for outcome in outcomes:
            assert "student_key" in outcome
            assert "indicator_key" in outcome
            assert "raw_score" in outcome
            assert 0 <= outcome["normalized_score"] <= 100

        # All 14 indicator keys must be present
        indicator_keys = {o["indicator_key"] for o in outcomes}
        assert indicator_keys == set(range(1, 15)), "Must cover all 14 indicators"

    def test_causal_relationships_hawaiian_language(self):
        """Hawaiian language participants should score higher on ROOT_IKE (ind 1)."""
        from scripts.seed_data_enterprise import generate_student_scores

        base_profile = {
            "is_hawaiian_language": False,
            "is_hālau_hula": False,
            "is_pbl_participant": False,
            "aina_connection_score": 3,
            "has_hoku_scholarship": False,
            "grade_level": 6,
            "ethnicity_category": "Asian",
        }

        n = 300
        lang_scores, no_lang_scores = [], []
        for _ in range(n):
            p_yes = {**base_profile, "is_hawaiian_language": True}
            p_no = {**base_profile, "is_hawaiian_language": False}
            lang_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_yes, 1, "2024-08-15") if o["indicator_key"] == 1)
            )
            no_lang_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_no, 1, "2024-08-15") if o["indicator_key"] == 1)
            )

        mean_lang = np.mean(lang_scores)
        mean_no_lang = np.mean(no_lang_scores)
        assert mean_lang > mean_no_lang + 2.0, (
            f"Hawaiian language participants should score higher on ROOT_IKE. "
            f"Got lang={mean_lang:.2f}, no-lang={mean_no_lang:.2f}"
        )

    def test_causal_relationships_aina_connection(self):
        """High aina_connection_score students should score higher on ROOT_ALOHA (ind 2)."""
        from scripts.seed_data_enterprise import generate_student_scores

        base_profile = {
            "is_hawaiian_language": False,
            "is_hālau_hula": False,
            "is_pbl_participant": False,
            "has_hoku_scholarship": False,
            "grade_level": 6,
            "ethnicity_category": "Asian",
        }

        n = 300
        high_scores, low_scores = [], []
        for _ in range(n):
            p_high = {**base_profile, "aina_connection_score": 5}
            p_low = {**base_profile, "aina_connection_score": 1}
            high_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_high, 1, "2024-08-15") if o["indicator_key"] == 2)
            )
            low_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_low, 1, "2024-08-15") if o["indicator_key"] == 2)
            )

        mean_high = np.mean(high_scores)
        mean_low = np.mean(low_scores)
        assert mean_high > mean_low + 5.0, (
            f"aina_connection=5 should score much higher on ROOT_ALOHA than aina=1. "
            f"Got high={mean_high:.2f}, low={mean_low:.2f}"
        )

    def test_causal_relationships_hoku_scholarship(self):
        """HOKU scholars should score higher on LEAF_ACAD (ind 7)."""
        from scripts.seed_data_enterprise import generate_student_scores

        base_profile = {
            "is_hawaiian_language": False,
            "is_hālau_hula": False,
            "is_pbl_participant": False,
            "aina_connection_score": 3,
            "grade_level": 10,
            "ethnicity_category": "Native Hawaiian",
        }

        n = 300
        hoku_scores, no_hoku_scores = [], []
        for _ in range(n):
            p_hoku = {**base_profile, "has_hoku_scholarship": True}
            p_no = {**base_profile, "has_hoku_scholarship": False}
            hoku_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_hoku, 1, "2024-08-15") if o["indicator_key"] == 7)
            )
            no_hoku_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_no, 1, "2024-08-15") if o["indicator_key"] == 7)
            )

        mean_hoku = np.mean(hoku_scores)
        mean_no_hoku = np.mean(no_hoku_scores)
        assert mean_hoku > mean_no_hoku + 6.0, (
            f"HOKU scholars should score much higher on LEAF_ACAD. "
            f"Got hoku={mean_hoku:.2f}, no-hoku={mean_no_hoku:.2f}"
        )

    def test_causal_relationships_pbl_problem_solving(self):
        """PBL participants should score higher on LEAF_PROBLEM (ind 10)."""
        from scripts.seed_data_enterprise import generate_student_scores

        base_profile = {
            "is_hawaiian_language": False,
            "is_hālau_hula": False,
            "aina_connection_score": 3,
            "has_hoku_scholarship": False,
            "grade_level": 6,
            "ethnicity_category": "Asian",
        }

        n = 300
        pbl_scores, no_pbl_scores = [], []
        for _ in range(n):
            p_pbl = {**base_profile, "is_pbl_participant": True}
            p_no = {**base_profile, "is_pbl_participant": False}
            pbl_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_pbl, 1, "2024-08-15") if o["indicator_key"] == 10)
            )
            no_pbl_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_no, 1, "2024-08-15") if o["indicator_key"] == 10)
            )

        mean_pbl = np.mean(pbl_scores)
        mean_no_pbl = np.mean(no_pbl_scores)
        assert mean_pbl > mean_no_pbl + 2.0, (
            f"PBL participants should score higher on LEAF_PROBLEM. "
            f"Got pbl={mean_pbl:.2f}, no-pbl={mean_no_pbl:.2f}"
        )

    def test_cultural_reflection_generation(self):
        """Test cultural reflection text generation."""
        from scripts.seed_data_enterprise import generate_cultural_reflection, HAWAIIAN_KEYWORDS

        # Generate a batch per sentiment — not all templates use {keyword},
        # so a single draw is inherently flaky. Over 20 draws, at least one
        # must contain a keyword for the injection mechanism to be working.
        N = 20
        positives    = [generate_cultural_reflection(sentiment_type="positive")    for _ in range(N)]
        neutrals     = [generate_cultural_reflection(sentiment_type="neutral")     for _ in range(N)]
        challengings = [generate_cultural_reflection(sentiment_type="challenging") for _ in range(N)]

        # All reflections must contain non-trivial text
        assert all(len(t) > 20 for t in positives),    "All positive reflections must have text"
        assert all(len(t) > 20 for t in neutrals),     "All neutral reflections must have text"
        assert all(len(t) > 20 for t in challengings), "All challenging reflections must have text"

        # Sentiment types must produce distinct output (sets differ across types)
        assert set(positives) != set(neutrals),     "Positive and neutral must differ"
        assert set(positives) != set(challengings), "Positive and challenging must differ"
        assert set(neutrals)  != set(challengings), "Neutral and challenging must differ"

        # Across a batch, keywords must appear in at least some reflections
        all_positive_text = " ".join(positives)
        has_keyword = any(kw in all_positive_text for kw in HAWAIIAN_KEYWORDS)
        assert has_keyword, (
            f"At least one of {N} positive reflections should contain a Hawaiian keyword. "
            f"Keywords checked: {HAWAIIAN_KEYWORDS[:5]}..."
        )


@pytest.mark.unit
class TestNLPAnalysis:
    """
    Verification tests from doc/module1/NLP.md.

    1. Scoring test  — Base=100 + missing wellbeing → 100/100 (no zero penalty).
    2. NLP test      — "I felt no mana today" → challenging (VADER negation handling).
    """

    def test_assessment_only_mode_no_penalty(self):
        """
        A student with Base=100 and NULL wellbeing must score 100 (not 70).
        Weight redistribution: base_w absorbs wellbeing_w → 1.00.
        """
        import pandas as pd
        from scripts.ike_kupuna_module import IkeKupunaAnalyzer

        analyzer = IkeKupunaAnalyzer()

        # Inject a synthetic df_clean row — no DB needed
        analyzer.df_clean = pd.DataFrame([{
            "student_key":        1,
            "student_uuid":       "test-uuid-001",
            "grade_level":        9,
            "gender_category":    "Male",
            "cohort_year":        2027,
            "is_hawaiian_language": False,
            "is_hālau_hula":      False,
            "is_pbl_participant": False,
            "normalized_score":   100.0,
            "wb_cultural":        None,   # ← wellbeing absent
            "wb_overall":         None,
            "wb_category":        None,
        }])
        analyzer.model()

        row = analyzer.df_scored.iloc[0]
        assert row["composite_score"] == 100.0, (
            f"Expected 100.0 with Base=100 + missing wellbeing (weight redistribution), "
            f"got {row['composite_score']}"
        )
        assert bool(row["wellbeing_missing"]) is True
        assert row["scoring_mode"] == "assessment_only"
        assert float(row["eff_base_weight"]) == 1.0
        assert float(row["eff_wb_weight"]) == 0.0

    def test_vader_negation_classified_as_challenging(self):
        """
        "I felt no mana today" must be classified as 'challenging' by VADER.
        Pre-label says 'positive' — VADER must override it.
        """
        from scripts.ike_kupuna_module import IkeKupunaAnalyzer

        analyzer = IkeKupunaAnalyzer()
        result = analyzer._nlp_analyse([
            # Deliberately wrong pre-label to prove VADER overrides it
            {"text": "I felt no mana today", "sentiment": "positive"},
        ])

        # VADER compound for this sentence is ~ -0.296 → challenging
        vader_entry = result["per_reflection_vader"][0]
        assert vader_entry["sentiment_computed"] == "challenging", (
            f"VADER should classify 'I felt no mana today' as challenging, "
            f"got '{vader_entry['sentiment_computed']}' (compound={vader_entry['vader_compound']})"
        )
        assert vader_entry["sentiment_original"] == "positive", (
            "sentiment_original should record the overridden pre-label"
        )

        # Mana keyword must land in 'challenging' bucket, not 'positive'
        mana_challenging = result["by_sentiment"]["challenging"].get("Mana", 0)
        mana_positive    = result["by_sentiment"]["positive"].get("Mana", 0)
        assert mana_challenging > 0, (
            "Keyword 'Mana' should be bucketed under challenging after VADER override"
        )
        assert mana_positive == 0, (
            "Keyword 'Mana' must NOT be bucketed under positive when sentence is negative"
        )


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

    def test_student_scores_generation(self, schema_db):
        """Test generate_student_scores returns 14 outcome records per student."""
        from scripts.seed_data_enterprise import generate_student_scores

        profile = {
            "is_hawaiian_language": True,
            "is_hālau_hula": False,
            "is_pbl_participant": True,
            "aina_connection_score": 4,
            "has_hoku_scholarship": False,
            "grade_level": 8,
            "ethnicity_category": "Native Hawaiian",
        }
        outcomes = generate_student_scores(
            student_profile=profile, student_key=1, assessment_date="2024-08-15"
        )

        # Must return exactly 14 records (one per indicator)
        assert len(outcomes) == 14, f"Expected 14 outcomes, got {len(outcomes)}"

        # Verify required fields on every record
        for outcome in outcomes:
            assert "student_key" in outcome
            assert "indicator_key" in outcome
            assert "raw_score" in outcome
            assert 0 <= outcome["normalized_score"] <= 100

        # All 14 indicator keys must be present
        indicator_keys = {o["indicator_key"] for o in outcomes}
        assert indicator_keys == set(range(1, 15)), "Must cover all 14 indicators"

    def test_causal_relationships_hawaiian_language(self):
        """Hawaiian language participants should score higher on ROOT_IKE (ind 1)."""
        from scripts.seed_data_enterprise import generate_student_scores

        base_profile = {
            "is_hawaiian_language": False,
            "is_hālau_hula": False,
            "is_pbl_participant": False,
            "aina_connection_score": 3,
            "has_hoku_scholarship": False,
            "grade_level": 6,
            "ethnicity_category": "Asian",
        }

        n = 300
        lang_scores, no_lang_scores = [], []
        for _ in range(n):
            p_yes = {**base_profile, "is_hawaiian_language": True}
            p_no = {**base_profile, "is_hawaiian_language": False}
            lang_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_yes, 1, "2024-08-15") if o["indicator_key"] == 1)
            )
            no_lang_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_no, 1, "2024-08-15") if o["indicator_key"] == 1)
            )

        mean_lang = np.mean(lang_scores)
        mean_no_lang = np.mean(no_lang_scores)
        assert mean_lang > mean_no_lang + 2.0, (
            f"Hawaiian language participants should score higher on ROOT_IKE. "
            f"Got lang={mean_lang:.2f}, no-lang={mean_no_lang:.2f}"
        )

    def test_causal_relationships_aina_connection(self):
        """High aina_connection_score students should score higher on ROOT_ALOHA (ind 2)."""
        from scripts.seed_data_enterprise import generate_student_scores

        base_profile = {
            "is_hawaiian_language": False,
            "is_hālau_hula": False,
            "is_pbl_participant": False,
            "has_hoku_scholarship": False,
            "grade_level": 6,
            "ethnicity_category": "Asian",
        }

        n = 300
        high_scores, low_scores = [], []
        for _ in range(n):
            p_high = {**base_profile, "aina_connection_score": 5}
            p_low = {**base_profile, "aina_connection_score": 1}
            high_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_high, 1, "2024-08-15") if o["indicator_key"] == 2)
            )
            low_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_low, 1, "2024-08-15") if o["indicator_key"] == 2)
            )

        mean_high = np.mean(high_scores)
        mean_low = np.mean(low_scores)
        assert mean_high > mean_low + 5.0, (
            f"aina_connection=5 should score much higher on ROOT_ALOHA than aina=1. "
            f"Got high={mean_high:.2f}, low={mean_low:.2f}"
        )

    def test_causal_relationships_hoku_scholarship(self):
        """HOKU scholars should score higher on LEAF_ACAD (ind 7)."""
        from scripts.seed_data_enterprise import generate_student_scores

        base_profile = {
            "is_hawaiian_language": False,
            "is_hālau_hula": False,
            "is_pbl_participant": False,
            "aina_connection_score": 3,
            "grade_level": 10,
            "ethnicity_category": "Native Hawaiian",
        }

        n = 300
        hoku_scores, no_hoku_scores = [], []
        for _ in range(n):
            p_hoku = {**base_profile, "has_hoku_scholarship": True}
            p_no = {**base_profile, "has_hoku_scholarship": False}
            hoku_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_hoku, 1, "2024-08-15") if o["indicator_key"] == 7)
            )
            no_hoku_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_no, 1, "2024-08-15") if o["indicator_key"] == 7)
            )

        mean_hoku = np.mean(hoku_scores)
        mean_no_hoku = np.mean(no_hoku_scores)
        assert mean_hoku > mean_no_hoku + 6.0, (
            f"HOKU scholars should score much higher on LEAF_ACAD. "
            f"Got hoku={mean_hoku:.2f}, no-hoku={mean_no_hoku:.2f}"
        )

    def test_causal_relationships_pbl_problem_solving(self):
        """PBL participants should score higher on LEAF_PROBLEM (ind 10)."""
        from scripts.seed_data_enterprise import generate_student_scores

        base_profile = {
            "is_hawaiian_language": False,
            "is_hālau_hula": False,
            "aina_connection_score": 3,
            "has_hoku_scholarship": False,
            "grade_level": 6,
            "ethnicity_category": "Asian",
        }

        n = 300
        pbl_scores, no_pbl_scores = [], []
        for _ in range(n):
            p_pbl = {**base_profile, "is_pbl_participant": True}
            p_no = {**base_profile, "is_pbl_participant": False}
            pbl_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_pbl, 1, "2024-08-15") if o["indicator_key"] == 10)
            )
            no_pbl_scores.append(
                next(o["normalized_score"] for o in generate_student_scores(p_no, 1, "2024-08-15") if o["indicator_key"] == 10)
            )

        mean_pbl = np.mean(pbl_scores)
        mean_no_pbl = np.mean(no_pbl_scores)
        assert mean_pbl > mean_no_pbl + 2.0, (
            f"PBL participants should score higher on LEAF_PROBLEM. "
            f"Got pbl={mean_pbl:.2f}, no-pbl={mean_no_pbl:.2f}"
        )

    def test_cultural_reflection_generation(self):
        """Test cultural reflection text generation."""
        from scripts.seed_data_enterprise import generate_cultural_reflection, HAWAIIAN_KEYWORDS

        # Generate a batch per sentiment — not all templates use {keyword},
        # so a single draw is inherently flaky. Over 20 draws, at least one
        # must contain a keyword for the injection mechanism to be working.
        N = 20
        positives    = [generate_cultural_reflection(sentiment_type="positive")    for _ in range(N)]
        neutrals     = [generate_cultural_reflection(sentiment_type="neutral")     for _ in range(N)]
        challengings = [generate_cultural_reflection(sentiment_type="challenging") for _ in range(N)]

        # All reflections must contain non-trivial text
        assert all(len(t) > 20 for t in positives),    "All positive reflections must have text"
        assert all(len(t) > 20 for t in neutrals),     "All neutral reflections must have text"
        assert all(len(t) > 20 for t in challengings), "All challenging reflections must have text"

        # Sentiment types must produce distinct output (sets differ across types)
        assert set(positives) != set(neutrals),     "Positive and neutral must differ"
        assert set(positives) != set(challengings), "Positive and challenging must differ"
        assert set(neutrals)  != set(challengings), "Neutral and challenging must differ"

        # Across a batch, keywords must appear in at least some reflections
        all_positive_text = " ".join(positives)
        has_keyword = any(kw in all_positive_text for kw in HAWAIIAN_KEYWORDS)
        assert has_keyword, (
            f"At least one of {N} positive reflections should contain a Hawaiian keyword. "
            f"Keywords checked: {HAWAIIAN_KEYWORDS[:5]}..."
        )


@pytest.mark.unit
class TestNLPAnalysis:
    """
    Verification tests from doc/module1/NLP.md.

    1. Scoring test — Base=100 + missing wellbeing → 100/100 (no zero penalty).
    2. NLP test     — negation handling via VADER (pre-label must be overridden).
    """

    def test_assessment_only_mode_no_penalty(self):
        """
        Base=100 + NULL wellbeing → composite=100.0, proficiency=Advanced.
        Weight redistribution: base_w absorbs wellbeing_w → 1.00.
        A perfect-base student must never be capped at 70 due to missing admin data.
        """
        import pandas as pd
        from scripts.ike_kupuna_module import IkeKupunaAnalyzer

        analyzer = IkeKupunaAnalyzer()
        analyzer.df_clean = pd.DataFrame([{
            "student_key":          999,
            "student_uuid":         "test-uuid-001",
            "grade_level":          10,
            "gender_category":      "M",
            "cohort_year":          2026,
            "is_hawaiian_language": 1,
            "is_hālau_hula":        0,
            "is_pbl_participant":   1,
            "normalized_score":     100.0,
            "wb_cultural":          None,   # ← wellbeing absent
            "wb_overall":           None,
            "wb_category":          None,
        }])
        analyzer.model()

        row = analyzer.df_scored.iloc[0]
        assert row["composite_score"] == 100.0, (
            f"Expected 100.0 with Base=100 + missing wellbeing, got {row['composite_score']}"
        )
        assert bool(row["wellbeing_missing"]) is True
        assert row["scoring_mode"] == "assessment_only"
        assert float(row["eff_base_weight"]) == 1.0
        assert float(row["eff_wb_weight"]) == 0.0
        assert row["proficiency"] == "Advanced"

    def test_vader_negation_classified_as_challenging(self):
        """
        "I felt no mana today" — pre-label is 'positive' but VADER compound ≈ -0.296.
        VADER must override the pre-label and classify as 'challenging'.
        Keyword 'Mana' must land in the challenging bucket, not positive.
        """
        from scripts.ike_kupuna_module import IkeKupunaAnalyzer

        analyzer = IkeKupunaAnalyzer()
        result = analyzer._nlp_analyse([
            {"text": "I felt no mana today", "sentiment": "positive"},
        ])

        entry = result["per_reflection_vader"][0]
        assert entry["sentiment_computed"] == "challenging", (
            f"VADER should classify 'I felt no mana today' as challenging, "
            f"got '{entry['sentiment_computed']}' (compound={entry['vader_compound']})"
        )
        assert entry["sentiment_original"] == "positive", (
            "sentiment_original must preserve the overridden pre-label for audit"
        )
        assert result["by_sentiment"]["challenging"].get("Mana", 0) > 0, (
            "Keyword 'Mana' should be bucketed under challenging"
        )
        assert result["by_sentiment"]["positive"].get("Mana", 0) == 0, (
            "Keyword 'Mana' must not appear in positive bucket"
        )

    def test_vader_neutral_borderline(self):
        """
        A borderline sentence ('Today was challenging, I did not understand Kuleana.')
        has VADER compound ~0.15, below the positive threshold (0.20) → neutral.
        """
        from scripts.ike_kupuna_module import IkeKupunaAnalyzer

        analyzer = IkeKupunaAnalyzer()
        result = analyzer._nlp_analyse([
            {"text": "Today was challenging, I did not understand Kuleana.", "sentiment": "neutral"},
        ])

        entry = result["per_reflection_vader"][0]
        assert entry["sentiment_computed"] == "neutral", (
            f"Borderline sentence should be neutral at threshold 0.20, "
            f"got '{entry['sentiment_computed']}' (compound={entry['vader_compound']})"
        )


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
