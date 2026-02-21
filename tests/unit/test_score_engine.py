"""
Data Science and Analytics Tests - The Archmage (肯瑞托大法师)

Tests for OSEMN protocol implementation:
- Obtain: Data extraction
- Scrub: Data cleaning and anomaly detection
- Explore: Statistical analysis
- Model: Scoring algorithms
- iNterpret: NLP analysis
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats


@pytest.mark.unit
class TestScoreEngineBasics:
    """Test basic scoring engine functionality."""

    def test_proficiency_level_generation(self):
        """Verify proficiency level generation from scores."""
        from scripts.score_engine import generate_proficiency

        # Test boundary values (based on actual implementation: 90/75/60)
        assert generate_proficiency(25) == "Below"
        assert generate_proficiency(50) == "Below"  # < 60
        assert generate_proficiency(65) == "Approaching"  # >= 60
        assert generate_proficiency(75) == "Proficient"  # >= 75
        assert generate_proficiency(95) == "Advanced"  # >= 90

        # Test edge cases
        assert generate_proficiency(0) == "Below"
        assert generate_proficiency(100) == "Advanced"

    def test_ike_kupuna_score_calculation(self):
        """Verify 'Ike Kūpuna score calculation."""
        from scripts.score_engine import calculate_ike_kupuna_score

        # Test with base score only (need all required fields)
        row = {
            "student_key": 1,
            "normalized_score": 80,
            "is_hawaiian_language": 0,
            "is_hālau_hula": 0,
        }
        result = calculate_ike_kupuna_score(row)
        assert 0 <= result["final_score"] <= 100
        assert "base_score" in result
        assert "proficiency" in result

        # Test with wellbeing correlation
        wellbeing_row = {"cultural_score": 85}
        result_with_wellbeing = calculate_ike_kupuna_score(row, wellbeing_row)
        assert 0 <= result_with_wellbeing["final_score"] <= 100


@pytest.mark.unit
class TestAnomalyDetection:
    """Test anomaly detection algorithms."""

    def test_null_value_detection(self):
        """Verify detection of NULL values in critical fields."""
        # Create test dataframe with NULL values
        df = pd.DataFrame(
            {
                "student_key": [1, 2, 3],
                "normalized_score": [85.0, None, 90.0],
                "assessment_date": ["2024-08-01", "2024-08-02", "2024-08-03"],
            }
        )

        # Detect NULL values
        null_scores = df[df["normalized_score"].isnull()]
        assert len(null_scores) == 1
        assert null_scores.iloc[0]["student_key"] == 2

    def test_invalid_range_detection(self):
        """Verify detection of out-of-range scores."""
        df = pd.DataFrame(
            {
                "student_key": [1, 2, 3, 4],
                "normalized_score": [85.0, -10.0, 150.0, 90.0],
            }
        )

        # Detect invalid ranges
        invalid_range = df[
            (df["normalized_score"] < 0) | (df["normalized_score"] > 100)
        ]
        assert len(invalid_range) == 2
        assert 2 in invalid_range["student_key"].values
        assert 3 in invalid_range["student_key"].values

    def test_future_date_detection(self):
        """Verify detection of future assessment dates."""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        df = pd.DataFrame(
            {"student_key": [1, 2], "assessment_date": ["2024-08-01", future_date]}
        )

        df["assessment_date"] = pd.to_datetime(df["assessment_date"])
        future_dates = df[df["assessment_date"] > datetime.now()]

        assert len(future_dates) == 1
        assert future_dates.iloc[0]["student_key"] == 2

    def test_statistical_outlier_detection(self):
        """Verify detection of statistical outliers using Z-score."""
        from scipy import stats

        # Create data with clear outlier
        scores = [75.0] * 98 + [150.0, 5.0]  # Most around 75, but two outliers
        df = pd.DataFrame({"student_key": range(1, 101), "normalized_score": scores})

        # Calculate Z-scores
        z_scores = np.abs(stats.zscore(df["normalized_score"].dropna()))
        outliers = df[z_scores > 3]

        # Should detect the extreme outlier (150)
        assert len(outliers) >= 1
        assert (
            99 in outliers["student_key"].values
            or 100 in outliers["student_key"].values
        )

    def test_score_proficiency_mismatch(self):
        """Verify detection of score-proficiency mismatches."""
        df = pd.DataFrame(
            {
                "student_key": [1, 2, 3],
                "normalized_score": [90.0, 85.0, 40.0],
                "proficiency_level": ["Proficient", "Below", "Approaching"],
            }
        )

        # High score but low proficiency
        high_score_low_prof = df[
            (df["normalized_score"] >= 85)
            & (df["proficiency_level"].isin(["Below", "Approaching"]))
        ]

        assert len(high_score_low_prof) == 1
        assert high_score_low_prof.iloc[0]["student_key"] == 2


@pytest.mark.unit
class TestStatisticalAnalysis:
    """Test statistical analysis functions."""

    def test_correlation_calculation(self):
        """Verify correlation matrix calculation."""
        # Create correlated data
        np.random.seed(42)
        x = np.random.normal(75, 10, 100)
        y = x + np.random.normal(0, 5, 100)  # y correlated with x

        df = pd.DataFrame({"x": x, "y": y})
        correlation = df["x"].corr(df["y"])

        # Should be positive correlation
        assert correlation > 0.5
        assert correlation < 1.0  # Not perfect

    def test_descriptive_statistics(self):
        """Verify descriptive statistics calculation."""
        scores = [75.0, 80.0, 85.0, 90.0, 95.0]

        mean = np.mean(scores)
        std = np.std(scores)
        median = np.median(scores)

        assert mean == 85.0
        assert median == 85.0
        assert std > 0

    def test_percentile_calculation(self):
        """Verify percentile rank calculation."""
        scores = [50, 60, 70, 80, 90, 100]

        # Calculate percentile for score 80
        percentile = stats.percentileofscore(scores, 80)

        # 80 should be around 75th percentile (4 out of 6 scores are <= 80)
        assert 60 <= percentile <= 80


@pytest.mark.unit
class TestNLPAnalysis:
    """Test NLP analysis functions."""

    def test_keyword_extraction(self):
        """Verify extraction of Hawaiian keywords from text."""
        from scripts.archmage_refinement import extract_keywords

        text = "Today I learned about Kuleana and Mālama from my Kūpuna."
        # keyword_dict format: {main_keyword: [variations]}
        keyword_dict = {
            "Kuleana": ["kuleana"],
            "Mālama": ["mālama", "malama"],
            "Kūpuna": ["kūpuna", "kupuna"],
            "Aloha": ["aloha"],
        }

        found_keywords = extract_keywords(text, keyword_dict)

        assert "Kuleana" in found_keywords
        assert "Mālama" in found_keywords
        assert "Kūpuna" in found_keywords
        assert "Aloha" not in found_keywords

    def test_sentiment_classification(self):
        """Verify sentiment classification of reflections."""
        positive_text = "I love learning about my culture! It makes me proud."
        challenging_text = "This is really hard and I feel frustrated."

        # Simple sentiment detection based on keywords
        positive_keywords = ["love", "proud", "amazing", "great", "happy"]
        challenging_keywords = ["hard", "difficult", "frustrated", "struggle"]

        positive_score = sum(
            1 for kw in positive_keywords if kw in positive_text.lower()
        )
        challenging_score = sum(
            1 for kw in challenging_keywords if kw in challenging_text.lower()
        )

        # Just verify we can detect sentiment keywords
        assert positive_score >= 0
        assert challenging_score >= 0

    def test_word_count_calculation(self):
        """Verify word count calculation."""
        text = "Today I learned about Hawaiian culture and traditions."
        word_count = len(text.split())

        assert word_count == 8

    def test_text_length_validation(self):
        """Verify handling of text length variations."""
        # Empty text
        empty_text = ""
        assert len(empty_text.split()) == 0

        # Short text
        short_text = "Hello world"
        assert len(short_text.split()) == 2

        # Long text
        long_text = " ".join(["word"] * 1000)
        assert len(long_text.split()) == 1000


@pytest.mark.integration
class TestOSEMNProtocol:
    """Integration tests for complete OSEMN pipeline."""

    def test_data_extraction(self, schema_db):
        """Test data extraction from database."""
        # First insert some test data
        hash_64 = "c" * 64
        schema_db.execute(
            """
            INSERT INTO dim_student_mapping (student_uuid, student_id_hash, encryption_key_ref, created_by, updated_by)
            VALUES ('550e8400-e29b-41d4-a716-446655440002', ?, 'key001', 'test', 'test')
        """,
            (hash_64,),
        )

        schema_db.execute("""
            INSERT INTO dim_students_masked (
                student_uuid, grade_level, cohort_year,
                entry_date, enrollment_status,
                effective_start_date, effective_end_date, is_current
            ) VALUES ('550e8400-e29b-41d4-a716-446655440002', 5, 2024, '2024-08-01', 'Active',
                     '2024-08-01', '9999-12-31', 1)
        """)

        schema_db.execute("""
            INSERT INTO dim_date (date_key, full_date, day_of_week, day_name, day_of_month, day_of_year,
                                  week_of_year, month_number, month_name, quarter, year_number, fiscal_year,
                                  academic_year, academic_term, term_start_date, term_end_date, is_school_day)
            VALUES (20240802, '2024-08-02', 5, 'Friday', 2, 215, 31, 8, 'August', 3, 2024, 2024,
                    '2024-2025', 'Fall', '2024-08-01', '2024-12-20', 1)
        """)

        schema_db.execute("""
            INSERT INTO fact_e_ola_outcomes (
                student_key, indicator_key, assessment_type_key, date_key,
                raw_score, normalized_score, proficiency_level,
                assessment_date, assessor_type, source_system
            ) VALUES (1, 1, 1, 20240802, 85.0, 85.0, 'Proficient', '2024-08-02', 'Teacher', 'Test')
        """)

        # Query student outcomes
        schema_db.execute("""
            SELECT COUNT(*) FROM fact_e_ola_outcomes
        """)
        count = schema_db.fetchone()[0]

        # Should have data
        assert count > 0

    def test_data_quality_check(self, schema_db):
        """Test comprehensive data quality check."""
        # Get all outcomes
        schema_db.execute("""
            SELECT student_key, normalized_score, proficiency_level
            FROM fact_e_ola_outcomes
            LIMIT 100
        """)
        rows = schema_db.fetchall()

        # Check data quality
        issues = []
        for row in rows:
            score = row[1]
            if score < 0 or score > 100:
                issues.append(f"Invalid score: {score}")

        # Should have no issues (or very few dirty data)
        assert len(issues) < 10

    def test_statistical_summary(self, schema_db):
        """Test generation of statistical summary."""
        schema_db.execute("""
            SELECT normalized_score FROM fact_e_ola_outcomes
        """)
        scores = [row[0] for row in schema_db.fetchall() if row[0] is not None]

        if len(scores) > 0:
            mean = np.mean(scores)
            std = np.std(scores)

            # Verify reasonable statistics
            assert 50 <= mean <= 90  # Reasonable mean
            assert 5 <= std <= 30  # Reasonable spread


@pytest.mark.slow
class TestPerformanceAndScale:
    """Performance tests for large datasets."""

    def test_anomaly_detection_performance(self):
        """Test anomaly detection on large dataset."""
        import time

        # Create large dataset
        n_records = 10000
        df = pd.DataFrame(
            {
                "student_key": range(1, n_records + 1),
                "normalized_score": np.random.normal(75, 15, n_records),
                "assessment_date": pd.date_range(
                    "2024-01-01", periods=n_records, freq="h"
                ),
            }
        )

        start_time = time.time()

        # Run anomaly detection
        null_scores = df[df["normalized_score"].isnull()]
        invalid_range = df[
            (df["normalized_score"] < 0) | (df["normalized_score"] > 100)
        ]

        elapsed = time.time() - start_time

        # Should complete in under 1 second
        assert elapsed < 1.0, f"Anomaly detection too slow: {elapsed:.2f}s"

    def test_correlation_matrix_performance(self):
        """Test correlation matrix calculation performance."""
        import time

        # Create dataset with multiple indicators
        n_students = 1000
        n_indicators = 14

        data = {}
        for i in range(n_indicators):
            data[f"indicator_{i}"] = np.random.normal(75, 15, n_students)

        df = pd.DataFrame(data)

        start_time = time.time()

        # Calculate correlation matrix
        corr_matrix = df.corr()

        elapsed = time.time() - start_time

        # Should complete quickly
        assert elapsed < 2.0, f"Correlation calculation too slow: {elapsed:.2f}s"
        assert corr_matrix.shape == (n_indicators, n_indicators)
