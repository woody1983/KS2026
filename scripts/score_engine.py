#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E Ola! Analytics - 'Ike Kūpuna (Ancestral Wisdom) Score Engine
Author: The Archmage (肯瑞托大法师)
Protocol: OSEMN (Obtain, Scrub, Explore, Model, iNterpret)
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats
import json

# ============================================================================
# PHASE 1: OBTAIN (数据获取)
# ============================================================================

print("🔮 Archmage: Initiating OSEMN Protocol...")
print("=" * 80)
print("\n📚 PHASE 1: OBTAIN - Extracting raw mana from the database...")

conn = sqlite3.connect("e_ola_analytics.db")

# Query 1: Get all student outcomes for 'Ike Kūpuna (indicator_key = 1)
query_ike_kupuna = """
SELECT 
    s.student_key,
    s.student_uuid,
    s.grade_level,
    s.gender_category,
    s.ethnicity_category,
    s.is_hawaiian_language,
    s.is_hālau_hula,
    s.entry_date,
    o.raw_score,
    o.normalized_score,
    o.proficiency_level,
    o.percentile_rank,
    o.assessment_date,
    o.data_quality_flag
FROM dim_students_masked s
JOIN fact_e_ola_outcomes o ON s.student_key = o.student_key
WHERE o.indicator_key = 1  -- 'Ike Kūpuna
ORDER BY s.student_key
"""

df_ike = pd.read_sql_query(query_ike_kupuna, conn)
print(
    f"✓ Extracted {len(df_ike)} 'Ike Kūpuna records from {df_ike['student_key'].nunique()} students"
)

# Query 2: Get well-being cultural scores for correlation analysis
query_wellbeing = """
SELECT 
    student_key,
    cultural_score,
    overall_wellbeing_score,
    wellbeing_category
FROM fact_wellbeing_measurements
ORDER BY student_key
"""

df_wellbeing = pd.read_sql_query(query_wellbeing, conn)
print(f"✓ Extracted {len(df_wellbeing)} well-being measurements")

# Query 3: Get all indicators for a subset of students (for correlation matrix)
query_all_indicators = """
SELECT 
    s.student_key,
    i.indicator_code,
    i.indicator_name,
    i.tier_level,
    o.normalized_score
FROM dim_students_masked s
JOIN fact_e_ola_outcomes o ON s.student_key = o.student_key
JOIN dim_e_ola_indicators i ON o.indicator_key = i.indicator_key
WHERE s.student_key <= 50  -- First 50 students for detailed analysis
ORDER BY s.student_key, i.indicator_key
"""

df_all = pd.read_sql_query(query_all_indicators, conn)
print(f"✓ Extracted {len(df_all)} multi-indicator records for correlation analysis")

conn.close()

# ============================================================================
# PHASE 2: SCRUB (数据清洗)
# ============================================================================

print("\n" + "=" * 80)
print("🧹 PHASE 2: SCRUB - Purifying the data stream...")
print("=" * 80)

anomalies = []


def detect_anomalies(df):
    """Detect logical inconsistencies and data quality issues"""
    issues = []

    # Check 1: NULL values in critical fields
    null_scores = df[df["normalized_score"].isnull()]
    if len(null_scores) > 0:
        issues.append(
            {
                "type": "NULL_VALUES",
                "severity": "CRITICAL",
                "count": len(null_scores),
                "description": f"Found {len(null_scores)} records with NULL scores",
                "student_keys": null_scores["student_key"].tolist(),
            }
        )

    # Check 2: Out-of-range scores (should be 0-100)
    invalid_range = df[(df["normalized_score"] < 0) | (df["normalized_score"] > 100)]
    if len(invalid_range) > 0:
        issues.append(
            {
                "type": "INVALID_RANGE",
                "severity": "CRITICAL",
                "count": len(invalid_range),
                "description": f"Found {len(invalid_range)} records with scores outside 0-100 range",
                "student_keys": invalid_range["student_key"].tolist(),
                "values": invalid_range["normalized_score"].tolist(),
            }
        )

    # Check 3: Future dates
    df["assessment_date"] = pd.to_datetime(df["assessment_date"])
    future_dates = df[df["assessment_date"] > datetime.now()]
    if len(future_dates) > 0:
        issues.append(
            {
                "type": "FUTURE_DATE",
                "severity": "HIGH",
                "count": len(future_dates),
                "description": f"Found {len(future_dates)} records with future assessment dates",
                "student_keys": future_dates["student_key"].tolist(),
                "dates": future_dates["assessment_date"].tolist(),
            }
        )

    # Check 4: Entry date vs grade level inconsistency
    df["entry_date"] = pd.to_datetime(df["entry_date"])
    current_year = datetime.now().year

    for idx, row in df.iterrows():
        entry_year = row["entry_date"].year
        grade = row["grade_level"]

        # Expected entry year based on grade (assuming K = age 5)
        expected_entry = current_year - (grade + 5)

        # Allow 1 year tolerance for mid-year entries
        if abs(entry_year - expected_entry) > 2:
            issues.append(
                {
                    "type": "DATE_GRADE_MISMATCH",
                    "severity": "MEDIUM",
                    "count": 1,
                    "description": f"Student {row['student_key']}: Grade {grade} but entry year {entry_year} (expected ~{expected_entry})",
                    "student_key": row["student_key"],
                    "grade": grade,
                    "entry_year": entry_year,
                    "expected_year": expected_entry,
                }
            )

    # Check 5: Impossible proficiency combinations
    # High score but low proficiency level
    high_score_low_prof = df[
        (df["normalized_score"] >= 85)
        & (df["proficiency_level"].isin(["Below", "Approaching"]))
    ]
    if len(high_score_low_prof) > 0:
        issues.append(
            {
                "type": "SCORE_PROFICIENCY_MISMATCH",
                "severity": "MEDIUM",
                "count": len(high_score_low_prof),
                "description": f"Found {len(high_score_low_prof)} records with high scores (≥85) but low proficiency levels",
                "student_keys": high_score_low_prof["student_key"].tolist(),
            }
        )

    # Check 6: Statistical outliers (Z-score > 3)
    z_scores = np.abs(stats.zscore(df["normalized_score"].dropna()))
    outliers = df[z_scores > 3]
    if len(outliers) > 0:
        issues.append(
            {
                "type": "STATISTICAL_OUTLIER",
                "severity": "LOW",
                "count": len(outliers),
                "description": f"Found {len(outliers)} statistical outliers (|Z| > 3)",
                "student_keys": outliers["student_key"].tolist(),
                "scores": outliers["normalized_score"].tolist(),
            }
        )

    return issues


anomalies = detect_anomalies(df_ike)

print(f"\n🔍 Anomaly Detection Results:")
print("-" * 80)

critical_count = sum(1 for a in anomalies if a["severity"] == "CRITICAL")
high_count = sum(1 for a in anomalies if a["severity"] == "HIGH")
medium_count = sum(1 for a in anomalies if a["severity"] == "MEDIUM")
low_count = sum(1 for a in anomalies if a["severity"] == "LOW")

print(
    f"   CRITICAL: {critical_count} | HIGH: {high_count} | MEDIUM: {medium_count} | LOW: {low_count}"
)

if anomalies:
    print("\n📋 Detailed Anomaly Report:")
    for i, issue in enumerate(anomalies[:10], 1):  # Show first 10
        print(f"\n   [{i}] {issue['type']} ({issue['severity']})")
        print(f"       → {issue['description']}")
        if "student_keys" in issue and isinstance(issue["student_keys"], list):
            print(
                f"       → Affected students: {issue['student_keys'][:5]}{'...' if len(issue['student_keys']) > 5 else ''}"
            )

# Clean the data
df_clean = df_ike.copy()
initial_count = len(df_clean)

# Remove records with critical issues
critical_student_keys = set()
for issue in anomalies:
    if issue["severity"] == "CRITICAL":
        if "student_keys" in issue:
            if isinstance(issue["student_keys"], list):
                critical_student_keys.update(issue["student_keys"])
            else:
                critical_student_keys.add(issue["student_keys"])

df_clean = df_clean[~df_clean["student_key"].isin(critical_student_keys)]
removed_count = initial_count - len(df_clean)

print(f"\n✨ Data Cleaning Summary:")
print(f"   Initial records: {initial_count}")
print(f"   Removed (critical issues): {removed_count}")
print(f"   Clean records: {len(df_clean)}")

# ============================================================================
# PHASE 3: EXPLORE (探索性分析)
# ============================================================================

print("\n" + "=" * 80)
print("🔍 PHASE 3: EXPLORE - Unveiling the patterns...")
print("=" * 80)

# Statistical summary
print("\n📊 'Ike Kūpuna Score Distribution:")
print("-" * 80)
desc_stats = df_clean["normalized_score"].describe()
print(f"   Count:    {desc_stats['count']:.0f}")
print(f"   Mean:     {desc_stats['mean']:.2f}")
print(f"   Std Dev:  {desc_stats['std']:.2f}")
print(f"   Min:      {desc_stats['min']:.2f}")
print(f"   25%:      {desc_stats['25%']:.2f}")
print(f"   50%:      {desc_stats['50%']:.2f}")
print(f"   75%:      {desc_stats['75%']:.2f}")
print(f"   Max:      {desc_stats['max']:.2f}")

# Proficiency level distribution
print("\n📈 Proficiency Level Distribution:")
print("-" * 80)
prof_dist = df_clean["proficiency_level"].value_counts()
for level, count in prof_dist.items():
    pct = (count / len(df_clean)) * 100
    bar = "█" * int(pct / 2)
    print(f"   {level:15s}: {count:3d} ({pct:5.1f}%) {bar}")

# Grade level analysis
print("\n🎓 Score by Grade Level:")
print("-" * 80)
grade_stats = df_clean.groupby("grade_level")["normalized_score"].agg(
    ["mean", "std", "count"]
)
for grade, row in grade_stats.iterrows():
    print(
        f"   Grade {grade:2d}: μ={row['mean']:5.1f}, σ={row['std']:4.1f}, n={row['count']:3.0f}"
    )

# Program participation analysis
print("\n🌺 Cultural Program Participation Impact:")
print("-" * 80)

# Hawaiian language
hawaiian_stats = df_clean.groupby("is_hawaiian_language")["normalized_score"].mean()
print(f"   Hawaiian Language Program:")
hawaiian_participants = df_clean[df_clean["is_hawaiian_language"] == 1]
hawaiian_non = df_clean[df_clean["is_hawaiian_language"] == 0]
if len(hawaiian_participants) > 0:
    print(
        f"      Participants:     {hawaiian_stats.loc[1]:.2f} (n={len(hawaiian_participants)})"
    )
else:
    print(f"      Participants:     N/A (n=0)")
if len(hawaiian_non) > 0:
    print(
        f"      Non-participants: {hawaiian_stats.loc[0]:.2f} (n={len(hawaiian_non)})"
    )
    if len(hawaiian_participants) > 0:
        print(
            f"      Difference:       {hawaiian_stats.loc[1] - hawaiian_stats.loc[0]:+.2f}"
        )
else:
    print(f"      Non-participants: N/A (n=0)")

# Hula
hula_stats = df_clean.groupby("is_hālau_hula")["normalized_score"].mean()
print(f"\n   Hālau Hula:")
hula_participants = df_clean[df_clean["is_hālau_hula"] == 1]
hula_non = df_clean[df_clean["is_hālau_hula"] == 0]
if len(hula_participants) > 0:
    print(
        f"      Participants:     {hula_stats.loc[1]:.2f} (n={len(hula_participants)})"
    )
else:
    print(f"      Participants:     N/A (n=0)")
if len(hula_non) > 0:
    print(f"      Non-participants: {hula_stats.loc[0]:.2f} (n={len(hula_non)})")
    if len(hula_participants) > 0:
        print(f"      Difference:       {hula_stats.loc[1] - hula_stats.loc[0]:+.2f}")
else:
    print(f"      Non-participants: N/A (n=0)")

# Statistical significance test
from scipy.stats import ttest_ind

hawaiian_yes = df_clean[df_clean["is_hawaiian_language"] == True]["normalized_score"]
hawaiian_no = df_clean[df_clean["is_hawaiian_language"] == False]["normalized_score"]
t_stat, p_value = ttest_ind(hawaiian_yes, hawaiian_no)

print(f"\n📐 Statistical Significance (Hawaiian Language):")
print(f"   t-statistic: {t_stat:.3f}")
print(f"   p-value:     {p_value:.6f}")
print(f"   Significant: {'YES' if p_value < 0.05 else 'NO'} (α = 0.05)")

# Correlation with cultural well-being
print("\n🔗 Correlation with Cultural Well-being:")
print("-" * 80)
df_merged = pd.merge(df_clean, df_wellbeing, on="student_key", how="inner")
if len(df_merged) > 0:
    correlation = df_merged["normalized_score"].corr(df_merged["cultural_score"])
    print(f"   'Ike Kūpuna ↔ Cultural Well-being: r = {correlation:.3f}")

    # Interpretation
    if abs(correlation) >= 0.7:
        strength = "Strong"
    elif abs(correlation) >= 0.4:
        strength = "Moderate"
    else:
        strength = "Weak"
    direction = "positive" if correlation > 0 else "negative"
    print(f"   Interpretation: {strength} {direction} correlation")

# ============================================================================
# PHASE 4: MODEL (建模)
# ============================================================================

print("\n" + "=" * 80)
print("⚗️  PHASE 4: MODEL - Casting the scoring spell...")
print("=" * 80)

print("\n🧮 'Ike Kūpuna Score Engine v1.0")
print("-" * 80)

# Define the scoring formula
# Score = w1 × Base_Score + w2 × Program_Bonus + w3 × Wellbeing_Adjustment

# Weights (transparent and adjustable)
WEIGHTS = {
    "base_score": 0.60,  # 60% - Raw assessment score
    "program_bonus": 0.25,  # 25% - Cultural program participation
    "wellbeing_adjustment": 0.15,  # 15% - Cultural well-being correlation
}

print("\n📐 Scoring Formula:")
print(
    "   Score_ike_kupuna = w₁ × Base_Score + w₂ × Program_Bonus + w₃ × Wellbeing_Adjustment"
)
print(f"\n   Weights:")
print(f"      w₁ (Base Score):           {WEIGHTS['base_score']:.2f}")
print(f"      w₂ (Program Bonus):        {WEIGHTS['program_bonus']:.2f}")
print(f"      w₃ (Wellbeing Adjustment): {WEIGHTS['wellbeing_adjustment']:.2f}")
print(f"      Sum: {sum(WEIGHTS.values()):.2f}")


def calculate_ike_kupuna_score(row, wellbeing_row=None):
    """
    Calculate 'Ike Kūpuna score with full logic derivation

    Logic:
    1. Base score is normalized to 0-100 scale
    2. Program bonus adds up to 10 points for cultural engagement
    3. Well-being adjustment considers cultural dimension correlation
    """

    # Component 1: Base Score (60% weight)
    base_score = row["normalized_score"]
    weighted_base = base_score * WEIGHTS["base_score"]

    # Component 2: Program Bonus (25% weight)
    # Hawaiian language = +5 points, Hula = +3 points, Both = +10 points (capped)
    program_bonus = 0
    if row["is_hawaiian_language"]:
        program_bonus += 5
    if row["is_hālau_hula"]:
        program_bonus += 3
    program_bonus = min(program_bonus, 10)  # Cap at 10 points
    weighted_program = program_bonus * 10 * WEIGHTS["program_bonus"]  # Scale to 100

    # Component 3: Well-being Adjustment (15% weight)
    wellbeing_adj = 0
    if wellbeing_row is not None:
        # Normalize cultural score to -10 to +10 adjustment range
        cultural_score = wellbeing_row["cultural_score"]
        wellbeing_adj = ((cultural_score - 50) / 50) * 10  # -10 to +10
    weighted_wellbeing = (50 + wellbeing_adj) * WEIGHTS[
        "wellbeing_adjustment"
    ]  # Center at 50

    # Final Score
    final_score = weighted_base + weighted_program + weighted_wellbeing

    # Ensure 0-100 bounds
    final_score = max(0, min(100, final_score))

    return {
        "student_key": row["student_key"],
        "base_score": base_score,
        "weighted_base": weighted_base,
        "program_bonus": program_bonus,
        "weighted_program": weighted_program,
        "wellbeing_adj": wellbeing_adj,
        "weighted_wellbeing": weighted_wellbeing,
        "final_score": final_score,
        "proficiency": generate_proficiency(final_score),
    }


def generate_proficiency(score):
    """Convert score to proficiency level"""
    if score >= 90:
        return "Advanced"
    elif score >= 75:
        return "Proficient"
    elif score >= 60:
        return "Approaching"
    else:
        return "Below"


# Calculate scores for all students
print("\n📝 Calculating scores with full derivation...")
print("-" * 80)

results = []
sample_size = min(10, len(df_clean))  # Show detailed derivation for first 10

for idx, (_, row) in enumerate(df_clean.iterrows()):
    # Find corresponding well-being data
    wellbeing_row = None
    wb_match = df_wellbeing[df_wellbeing["student_key"] == row["student_key"]]
    if len(wb_match) > 0:
        wellbeing_row = wb_match.iloc[0]

    result = calculate_ike_kupuna_score(row, wellbeing_row)
    results.append(result)

    # Show detailed derivation for first N students
    if idx < sample_size:
        print(
            f"\n   Student {row['student_key']} ({row['gender_category']}, Grade {row['grade_level']}):"
        )
        print(
            f"      ├─ Base Score:           {result['base_score']:.1f} × {WEIGHTS['base_score']:.2f} = {result['weighted_base']:.2f}"
        )
        print(
            f"      ├─ Program Bonus:        {result['program_bonus']:.0f} pts × 10 × {WEIGHTS['program_bonus']:.2f} = {result['weighted_program']:.2f}"
        )
        if result["wellbeing_adj"] != 0:
            print(
                f"      ├─ Well-being Adj:       ({result['wellbeing_adj']:+.1f}) × {WEIGHTS['wellbeing_adjustment']:.2f} = {result['weighted_wellbeing']:.2f}"
            )
        else:
            print(f"      ├─ Well-being Adj:       N/A (no data)")
        print(
            f"      └─ FINAL SCORE:          {result['final_score']:.2f} → {result['proficiency']}"
        )

results_df = pd.DataFrame(results)

print(f"\n\n📊 Model Output Statistics:")
print("-" * 80)
print(f"   Mean Score:   {results_df['final_score'].mean():.2f}")
print(f"   Std Dev:      {results_df['final_score'].std():.2f}")
print(f"   Min:          {results_df['final_score'].min():.2f}")
print(f"   Max:          {results_df['final_score'].max():.2f}")

print(f"\n   Proficiency Distribution:")
prof_final = results_df["proficiency"].value_counts()
for level in ["Advanced", "Proficient", "Approaching", "Below"]:
    if level in prof_final:
        count = prof_final[level]
        pct = (count / len(results_df)) * 100
        print(f"      {level:12s}: {count:3d} ({pct:5.1f}%)")

# ============================================================================
# PHASE 5: INTERPRET (解释)
# ============================================================================

print("\n" + "=" * 80)
print("📖 PHASE 5: INTERPRET - Translating numbers to narratives...")
print("=" * 80)

# Generate insights for top and bottom performers
print("\n🌟 Top Performers (Advanced):")
print("-" * 80)
top_performers = results_df[results_df["proficiency"] == "Advanced"].head(5)
for _, student in top_performers.iterrows():
    orig_row = df_clean[df_clean["student_key"] == student["student_key"]].iloc[0]
    print(f"\n   Student {student['student_key']}: {student['final_score']:.1f} points")
    print(
        f"      → Strong base score ({student['base_score']:.1f}) indicates solid assessment performance"
    )
    if student["program_bonus"] > 0:
        programs = []
        if orig_row["is_hawaiian_language"]:
            programs.append("Hawaiian language")
        if orig_row["is_hālau_hula"]:
            programs.append("hula")
        print(
            f"      → Cultural engagement bonus (+{student['program_bonus']:.0f} pts) from {', '.join(programs)} participation"
        )
    if student["wellbeing_adj"] > 2:
        print(
            f"      → Positive cultural well-being correlation enhances overall score"
        )
    print(f"      → RECOMMENDATION: Consider as peer mentor for cultural programs")

print("\n\n⚠️  Students Needing Support (Below):")
print("-" * 80)
bottom_performers = results_df[results_df["proficiency"] == "Below"].head(5)
for _, student in bottom_performers.iterrows():
    orig_row = df_clean[df_clean["student_key"] == student["student_key"]].iloc[0]
    print(f"\n   Student {student['student_key']}: {student['final_score']:.1f} points")
    print(
        f"      → Base score ({student['base_score']:.1f}) suggests foundational gaps"
    )
    if student["program_bonus"] == 0:
        print(
            f"      → No cultural program participation detected - opportunity for engagement"
        )
    if student["wellbeing_adj"] < -2:
        print(f"      → Cultural well-being concerns may be impacting performance")
    print(f"      → RECOMMENDATION: Refer to cultural mentorship program")

# Generate program effectiveness insight
print("\n\n📈 Program Effectiveness Analysis:")
print("-" * 80)

# Merge results with student data for analysis
results_with_student = pd.merge(
    results_df,
    df_clean[["student_key", "is_hawaiian_language", "is_hālau_hula"]],
    on="student_key",
    how="left",
)

hawaiian_participants = results_with_student[
    results_with_student["is_hawaiian_language"] == 1
]["final_score"].mean()
hawaiian_non = results_with_student[results_with_student["is_hawaiian_language"] == 0][
    "final_score"
].mean()
print(f"   Hawaiian Language Program Impact:")
print(f"      Participants:     {hawaiian_participants:.2f} avg score")
print(f"      Non-participants: {hawaiian_non:.2f} avg score")
effect_size = hawaiian_participants - hawaiian_non
print(f"      Effect Size:      {effect_size:+.2f} points")
print(
    f"      → INTERPRETATION: {'Strong positive' if effect_size > 5 else 'Moderate positive' if effect_size > 2 else 'Minimal'} impact on 'Ike Kūpuna scores"
)

# ============================================================================
# OUTPUT GENERATION
# ============================================================================

print("\n" + "=" * 80)
print("💾 Generating Output Files...")
print("=" * 80)

# Save detailed results
output_data = []
for _, result in results_df.iterrows():
    orig_row = df_clean[df_clean["student_key"] == result["student_key"]].iloc[0]
    output_data.append(
        {
            "student_key": result["student_key"],
            "student_uuid": orig_row["student_uuid"],
            "grade_level": int(orig_row["grade_level"]),
            "gender": orig_row["gender_category"],
            "ethnicity": orig_row["ethnicity_category"],
            "base_score": round(result["base_score"], 2),
            "program_bonus": result["program_bonus"],
            "wellbeing_adjustment": round(result["wellbeing_adj"], 2),
            "final_score": round(result["final_score"], 2),
            "proficiency_level": result["proficiency"],
            "calculation_logic": f"{result['base_score']:.1f}×0.6 + {result['program_bonus']:.0f}×2.5 + {50 + result['wellbeing_adj']:.1f}×0.15",
        }
    )

output_df = pd.DataFrame(output_data)
output_df.to_csv("output/ike_kupuna_scores.csv", index=False)
print(f"✓ Saved detailed scores to: output/ike_kupuna_scores.csv")

# Save anomaly report
anomaly_report = {
    "analysis_timestamp": datetime.now().isoformat(),
    "total_records_analyzed": len(df_ike),
    "clean_records": len(df_clean),
    "anomalies_detected": len(anomalies),
    "anomaly_breakdown": {
        "critical": critical_count,
        "high": high_count,
        "medium": medium_count,
        "low": low_count,
    },
    "detailed_issues": anomalies,
}

with open("output/anomaly_report.json", "w") as f:
    json.dump(anomaly_report, f, indent=2, default=str)
print(f"✓ Saved anomaly report to: output/anomaly_report.json")

# Save model specification
model_spec = {
    "model_name": "IkeKupunaScoreEngine_v1",
    "timestamp": datetime.now().isoformat(),
    "formula": "Score = w₁×Base + w₂×Program_Bonus + w₃×Wellbeing_Adj",
    "weights": WEIGHTS,
    "components": {
        "base_score": {
            "description": "Normalized assessment score from fact_e_ola_outcomes",
            "weight": WEIGHTS["base_score"],
            "range": "0-100",
        },
        "program_bonus": {
            "description": "Cultural program participation bonus",
            "weight": WEIGHTS["program_bonus"],
            "calculation": "Hawaiian language (+5) + Hula (+3), capped at 10",
            "scaled_range": "0-25",
        },
        "wellbeing_adjustment": {
            "description": "Cultural well-being correlation adjustment",
            "weight": WEIGHTS["wellbeing_adjustment"],
            "calculation": "((cultural_score - 50) / 50) × 10",
            "range": "-10 to +10",
        },
    },
    "proficiency_thresholds": {
        "Advanced": 90,
        "Proficient": 75,
        "Approaching": 60,
        "Below": 0,
    },
    "statistics": {
        "mean_score": float(results_df["final_score"].mean()),
        "std_dev": float(results_df["final_score"].std()),
        "sample_size": len(results_df),
    },
}

with open("output/model_specification.json", "w") as f:
    json.dump(model_spec, f, indent=2)
print(f"✓ Saved model specification to: output/model_specification.json")

print("\n" + "=" * 80)
print("🔮 Archmage: OSEMN Protocol Complete!")
print("=" * 80)
print("\n📦 Deliverables for Lord of Rivendell:")
print("   1. output/ike_kupuna_scores.csv - Student scores with full derivation")
print("   2. output/anomaly_report.json - Data quality issues detected")
print("   3. output/model_specification.json - Transparent scoring algorithm")
print(
    "\n✨ The mana has been purified and channeled. Ready for narrative transformation."
)
print("=" * 80)
