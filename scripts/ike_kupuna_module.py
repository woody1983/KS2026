#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
'Ike Kūpuna (Ancestral Wisdom) Analysis Module
===============================================
Author  : The Archmage (肯瑞托大法师)
Protocol: OSEMN — Obtain · Scrub · Explore · Model · iNterpret
Indicator: ROOT_IKE (indicator_key = 1)

This module is the single source of truth for all 'Ike Kūpuna analytics.
It is designed to be importable, testable, and transparently reproducible.
No black-box logic. Every weight, every threshold, every decision is visible.

Usage:
    from scripts.ike_kupuna_module import IkeKupunaAnalyzer
    analyzer = IkeKupunaAnalyzer()
    report = analyzer.run()
"""

import json
import re
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DB_PATH = Path(__file__).parent.parent / "e_ola_enterprise.db"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

INDICATOR_KEY = 1           # ROOT_IKE — 'Ike Kūpuna
INDICATOR_CODE = "ROOT_IKE"
INDICATOR_NAME = "'Ike Kūpuna (Ancestral Wisdom)"

# Scoring formula weights (must sum to 1.0)
# NOTE: programme participation effects are encoded in normalized_score via the causal
# seed model. A separate program_bonus channel was removed to prevent double-counting.
WEIGHTS = {
    "base_score":           0.70,  # Raw normalized assessment score (encodes programme effects)
    "wellbeing_adjustment": 0.30,  # Cultural well-being correlation
}

# Programme bonus points (pre-scaling)
PROGRAMME_POINTS = {
    "hawaiian_language": 5,
    "halau_hula": 3,
    "pbl_participant": 2,
    "cap": 10,              # Maximum bonus points before scaling
}

# Proficiency thresholds
PROFICIENCY_THRESHOLDS = {
    "Advanced":   90,
    "Proficient": 75,
    "Approaching": 60,
    "Below":       0,
}

# Hawaiian cultural keywords for NLP
HAWAIIAN_KEYWORDS = {
    "Kūpuna":   ["kūpuna", "kupuna", "ancestors", "elders", "ancestral"],
    "Kuleana":  ["kuleana", "responsibility", "duty", "obligation"],
    "Mālama":   ["mālama", "malama", "care", "protect", "stewardship", "nurture"],
    "ʻĀina":    ["ʻāina", "aina", "land", "earth", "nature"],
    "Kalo":     ["kalo", "taro"],
    "Mana":     ["mana", "spiritual", "power", "energy"],
    "Laulima":  ["laulima", "cooperation", "together", "collaboration"],
    "Aloha":    ["aloha", "love", "compassion", "kindness"],
    "ʻŌlelo":   ["ʻōlelo", "olelo", "language", "hawaiian language"],
    "Waʻa":     ["waʻa", "waa", "canoe", "navigation", "hoʻokele"],
}

SAMPLE_REFLECTIONS = [
    {"text": "Today at the Loʻi kalo, I felt a strong connection to my Kūpuna. Planting kalo reminded me that our ancestors were very wise.", "sentiment": "positive"},
    {"text": "Working in Hula kahiko was amazing! Our culture teaches respect and humility. It makes me proud to be Hawaiian.", "sentiment": "positive"},
    {"text": "My Kūpuna taught me about breath control. I now understand why our traditions hold deep meaning — this is our kuleana.", "sentiment": "positive"},
    {"text": "During Waʻa practice I could feel the mana of our ancestors. Laulima makes us stronger.", "sentiment": "positive"},
    {"text": "Being in the Mālama ʻāina session made me feel connected to the ʻāina. The land provides for us if we care for it.", "sentiment": "positive"},
    {"text": "I helped classmates during Lauhala weaving. It felt good to practice laulima. We must mālama the land for future generations.", "sentiment": "positive"},
    {"text": "Today we learned about water quality in Fishpond restoration. Interesting, but I need more time to understand.", "sentiment": "neutral"},
    {"text": "We practiced ʻŌlelo Hawaiʻi for two hours. Pronunciation was okay — not too hard or too easy.", "sentiment": "neutral"},
    {"text": "Hoʻokele navigation was really hard today. I struggled with star patterns and felt frustrated.", "sentiment": "challenging"},
    {"text": "I don't understand why we need to learn Kuleana. It feels confusing and I want to give up.", "sentiment": "challenging"},
]


# ---------------------------------------------------------------------------
# IkeKupunaAnalyzer
# ---------------------------------------------------------------------------

class IkeKupunaAnalyzer:
    """
    Full OSEMN pipeline for the 'Ike Kūpuna indicator.

    Attributes
    ----------
    df_raw      : raw DataFrame from fact_e_ola_outcomes × dim_students_masked
    df_clean    : scrubbed DataFrame
    df_scored   : scored DataFrame with final composite scores
    anomalies   : list of detected data quality issues
    nlp_results : NLP keyword & sentiment analysis results
    report      : final JSON-serialisable report dict
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.df_raw: pd.DataFrame = pd.DataFrame()
        self.df_clean: pd.DataFrame = pd.DataFrame()
        self.df_scored: pd.DataFrame = pd.DataFrame()
        self.anomalies: list = []
        self.dropped_records_log: dict = {}
        self.nlp_results: dict = {}
        self.report: dict = {}

    # -----------------------------------------------------------------------
    # PHASE 1 — OBTAIN
    # -----------------------------------------------------------------------

    def obtain(self) -> "IkeKupunaAnalyzer":
        """Extract 'Ike Kūpuna data from enterprise database, including wellbeing scores."""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT
                s.student_key,
                s.student_uuid,
                s.grade_level,
                s.gender_category,
                s.ethnicity_category,
                s.cohort_year,
                s.homeroom_id,
                s.is_pbl_participant,
                s.is_hawaiian_language,
                s.is_hālau_hula,
                s.entry_date,
                o.outcome_id,
                o.raw_score,
                o.normalized_score,
                o.proficiency_level,
                o.percentile_rank,
                o.assessment_date,
                o.data_quality_flag,
                o.assessor_type,
                w.cultural_score         AS wb_cultural,
                w.overall_wellbeing_score AS wb_overall,
                w.wellbeing_category     AS wb_category
            FROM dim_students_masked s
            JOIN fact_e_ola_outcomes o
                ON s.student_key = o.student_key
            LEFT JOIN fact_wellbeing_measurements w
                ON s.student_key = w.student_key
            WHERE o.indicator_key = ?
              AND s.is_current = 1
            ORDER BY s.student_key
        """

        self.df_raw = pd.read_sql_query(query, conn, params=(INDICATOR_KEY,))
        conn.close()
        return self

    # -----------------------------------------------------------------------
    # PHASE 2 — SCRUB
    # -----------------------------------------------------------------------

    def scrub(self) -> "IkeKupunaAnalyzer":
        """Detect anomalies and produce a clean working dataset."""
        df = self.df_raw.copy()
        df["assessment_date"] = pd.to_datetime(df["assessment_date"], errors="coerce")
        df["entry_date"] = pd.to_datetime(df["entry_date"], errors="coerce")

        issues = []
        now = datetime.now()

        # 1. NULL scores
        null_mask = df["normalized_score"].isnull()
        if null_mask.any():
            issues.append({
                "type": "NULL_SCORE",
                "severity": "CRITICAL",
                "count": int(null_mask.sum()),
                "student_keys": df.loc[null_mask, "student_key"].tolist(),
                "description": f"{null_mask.sum()} records with NULL normalized_score",
            })

        # 2. Out-of-range scores (0–100)
        range_mask = (df["normalized_score"] < 0) | (df["normalized_score"] > 100)
        if range_mask.any():
            issues.append({
                "type": "OUT_OF_RANGE",
                "severity": "CRITICAL",
                "count": int(range_mask.sum()),
                "student_keys": df.loc[range_mask, "student_key"].tolist(),
                "values": df.loc[range_mask, "normalized_score"].tolist(),
                "description": f"{range_mask.sum()} scores outside 0–100 range",
            })

        # 3. Future assessment dates
        future_mask = df["assessment_date"] > now
        if future_mask.any():
            issues.append({
                "type": "FUTURE_DATE",
                "severity": "HIGH",
                "count": int(future_mask.sum()),
                "student_keys": df.loc[future_mask, "student_key"].tolist(),
                "description": f"{future_mask.sum()} records with future assessment dates",
            })

        # 4. Score ↔ proficiency mismatch
        def expected_proficiency(score):
            if score >= 90:  return "Advanced"
            if score >= 75:  return "Proficient"
            if score >= 60:  return "Approaching"
            return "Below"

        valid = df["normalized_score"].notnull()
        mismatch_mask = valid & (
            df.loc[valid, "proficiency_level"]
            != df.loc[valid, "normalized_score"].apply(expected_proficiency)
        )
        if mismatch_mask.any():
            issues.append({
                "type": "PROFICIENCY_MISMATCH",
                "severity": "MEDIUM",
                "count": int(mismatch_mask.sum()),
                "description": f"{mismatch_mask.sum()} records where proficiency label "
                               f"does not match score threshold",
            })

        # 5. Statistical outliers (|Z| > 3)
        scores = df["normalized_score"].dropna()
        if len(scores) > 3:
            z = np.abs(stats.zscore(scores))
            outlier_idx = scores.index[z > 3]
            if len(outlier_idx):
                issues.append({
                    "type": "STATISTICAL_OUTLIER",
                    "severity": "LOW",
                    "count": len(outlier_idx),
                    "student_keys": df.loc[outlier_idx, "student_key"].tolist(),
                    "scores": df.loc[outlier_idx, "normalized_score"].tolist(),
                    "description": f"{len(outlier_idx)} records with |Z-score| > 3",
                })

        self.anomalies = issues

        # Remove CRITICAL rows to produce clean dataset
        bad_keys: set = set()
        for issue in issues:
            if issue["severity"] == "CRITICAL":
                bad_keys.update(issue.get("student_keys", []))

        self.df_clean = df[~df["student_key"].isin(bad_keys)].copy()

        # Build dropped record log (Issue 6 — survivorship bias mitigation)
        n_dropped = len(df) - len(self.df_clean)
        self.dropped_records_log = {
            "total_extracted": len(df),
            "total_dropped":   n_dropped,
            "total_retained":  len(self.df_clean),
            "drop_rate_pct":   round(n_dropped / max(len(df), 1) * 100, 2),
            "reasons": [
                {
                    "type":        issue["type"],
                    "severity":    issue["severity"],
                    "count":       issue.get("count", 0),
                    "student_keys": issue.get("student_keys", []),
                    "description": issue["description"],
                }
                for issue in issues
                if issue["severity"] == "CRITICAL"
            ],
            "note": (
                "Records are dropped only for CRITICAL severity issues (NULL scores, "
                "out-of-range values). Non-critical anomalies (FUTURE_DATE, PROFICIENCY_MISMATCH, "
                "STATISTICAL_OUTLIER) are retained and flagged. If drop_rate_pct is high "
                "or non-random (e.g. low-performing students), this may indicate survivorship bias."
            ),
        }

        return self

    # -----------------------------------------------------------------------
    # PHASE 3 — EXPLORE
    # -----------------------------------------------------------------------

    def explore(self) -> dict:
        """Generate descriptive statistics across multiple dimensions."""
        df = self.df_clean

        # Overall distribution
        desc = df["normalized_score"].describe()
        distribution = {
            "count":  int(desc["count"]),
            "mean":   round(float(desc["mean"]), 2),
            "std":    round(float(desc["std"]), 2),
            "min":    round(float(desc["min"]), 2),
            "p25":    round(float(desc["25%"]), 2),
            "median": round(float(desc["50%"]), 2),
            "p75":    round(float(desc["75%"]), 2),
            "max":    round(float(desc["max"]), 2),
        }

        # Proficiency breakdown
        prof_counts = df["proficiency_level"].value_counts().to_dict()
        proficiency = {
            level: {
                "count": int(prof_counts.get(level, 0)),
                "pct": round(prof_counts.get(level, 0) / max(len(df), 1) * 100, 1),
            }
            for level in ["Advanced", "Proficient", "Approaching", "Below"]
        }

        # By grade level
        grade_stats = (
            df.groupby("grade_level")["normalized_score"]
            .agg(mean="mean", std="std", count="count")
            .round(2)
        )
        by_grade = {
            int(g): {"mean": row["mean"], "std": row["std"], "count": int(row["count"])}
            for g, row in grade_stats.iterrows()
        }

        # By gender
        gender_stats = (
            df.groupby("gender_category")["normalized_score"]
            .agg(mean="mean", count="count")
            .round(2)
        )
        by_gender = {
            g: {"mean": float(row["mean"]), "count": int(row["count"])}
            for g, row in gender_stats.iterrows()
        }

        # Programme participation impact
        def programme_comparison(col_name, label):
            yes = df[df[col_name] == 1]["normalized_score"]
            no  = df[df[col_name] == 0]["normalized_score"]
            effect = round(float(yes.mean() - no.mean()), 2) if len(yes) and len(no) else 0
            p_val  = None
            if len(yes) > 1 and len(no) > 1:
                _, p = stats.ttest_ind(yes, no)
                p_val = round(float(p), 6)
            return {
                "participants_mean":     round(float(yes.mean()), 2) if len(yes) else None,
                "participants_n":        int(len(yes)),
                "non_participants_mean": round(float(no.mean()), 2) if len(no) else None,
                "non_participants_n":    int(len(no)),
                "effect_size_pts":       effect,
                "p_value":               p_val,
                "significant":           (p_val is not None and p_val < 0.05),
            }

        programme_impact = {
            "hawaiian_language": programme_comparison("is_hawaiian_language", "Hawaiian Language"),
            "halau_hula":        programme_comparison("is_hālau_hula", "Hālau Hula"),
            "pbl_participant":   programme_comparison("is_pbl_participant", "PBL-by-Design"),
        }

        # Cohort trend (by cohort_year)
        cohort_stats = (
            df.groupby("cohort_year")["normalized_score"]
            .agg(mean="mean", count="count")
            .round(2)
        )
        cohort_trend = {
            int(y): {"mean": float(row["mean"]), "count": int(row["count"])}
            for y, row in cohort_stats.iterrows()
        }

        return {
            "distribution":      distribution,
            "proficiency":       proficiency,
            "by_grade":          by_grade,
            "by_gender":         by_gender,
            "programme_impact":  programme_impact,
            "cohort_trend":      cohort_trend,
        }

    # -----------------------------------------------------------------------
    # PHASE 4 — MODEL
    # -----------------------------------------------------------------------

    def model(self) -> "IkeKupunaAnalyzer":
        """
        Apply the 'Ike Kūpuna composite scoring formula to every student.

        Formula (both components present):
            Score = 0.70 × Base_Score + 0.30 × Wellbeing_Score

        Programme participation effects (Hawaiian language, hula, PBL) are already
        encoded in normalized_score via the causal seed model — no separate bonus
        channel is needed and adding one would double-count those effects.

        Wellbeing: uses wb_cultural (0–100) directly at 30% weight.

        WEIGHT REDISTRIBUTION (missing wellbeing):
            Score = 1.00 × Base_Score
        When wb_cultural is NULL/missing the wellbeing weight (0.30) is absorbed by
        base score rather than set to zero. Setting to zero would cap a perfect-base
        student at 70, creating an unfair -30 pt administrative penalty. Redistribution
        scores the student entirely on available data; the scoring_mode flag
        ("composite" vs "assessment_only") is preserved for downstream transparency.

        Clamped to [0, 100].
        """
        df = self.df_clean.copy()
        rows = []

        for _, row in df.iterrows():
            # Component 1 — Base Score
            base = float(row["normalized_score"])

            # Component 2 — Wellbeing
            wb_available = pd.notna(row.get("wb_cultural"))
            wellbeing_score = float(row["wb_cultural"]) if wb_available else 0.0
            wellbeing_missing = not wb_available

            # Effective weights — redistribute wellbeing weight to base when absent
            if not wellbeing_missing:
                eff_base_w = WEIGHTS["base_score"]            # 0.70
                eff_wb_w   = WEIGHTS["wellbeing_adjustment"]  # 0.30
            else:
                eff_base_w = 1.0   # absorbs the 0.30 wellbeing weight
                eff_wb_w   = 0.0

            w_base     = base          * eff_base_w
            w_wellbeing = wellbeing_score * eff_wb_w

            final = max(0.0, min(100.0, w_base + w_wellbeing))

            def proficiency(score):
                for level, threshold in sorted(
                    PROFICIENCY_THRESHOLDS.items(), key=lambda x: x[1], reverse=True
                ):
                    if score >= threshold:
                        return level
                return "Below"

            rows.append({
                "student_key":     row["student_key"],
                "student_uuid":    row["student_uuid"],
                "grade_level":     int(row["grade_level"]),
                "gender":          row["gender_category"],
                "cohort_year":     int(row["cohort_year"]),
                "is_hawaiian_language": bool(row["is_hawaiian_language"]),
                "is_halau_hula":   bool(row["is_hālau_hula"]),
                "is_pbl":          bool(row["is_pbl_participant"]),
                # Score components
                "raw_base_score":    round(base, 2),
                "wellbeing_score":   round(wellbeing_score, 2),
                "wellbeing_missing": wellbeing_missing,
                "scoring_mode":      "assessment_only" if wellbeing_missing else "composite",
                "eff_base_weight":   eff_base_w,
                "eff_wb_weight":     eff_wb_w,
                "weighted_base":     round(w_base, 3),
                "weighted_wellbeing": round(w_wellbeing, 3),
                "composite_score":   round(final, 2),
                "proficiency":       proficiency(final),
                "wb_overall_score":  round(float(row["wb_overall"]), 2) if pd.notna(row.get("wb_overall")) else None,
                "wb_category":       row.get("wb_category"),
                "formula_trace":     (
                    f"{base:.1f}×{eff_base_w:.2f}"
                    + (f" + {wellbeing_score:.1f}×{eff_wb_w:.2f}" if not wellbeing_missing else "  [wb missing → base_w=1.00]")
                    + f" = {final:.2f}"
                ),
            })

        self.df_scored = pd.DataFrame(rows)
        return self

    # -----------------------------------------------------------------------
    # PHASE 4b — NLP
    # -----------------------------------------------------------------------

    def _nlp_analyse(self, reflections: list[dict]) -> dict:
        """
        Keyword extraction + VADER-based sentiment classification on cultural reflections.

        Replaces pre-labeled sentiment fields with VADER compound scores so that
        negations ("I felt no mana today", "lacks kuleana") are classified correctly
        rather than defaulting to "neutral" or trusting a potentially mis-labeled tag.

        VADER classification thresholds (industry standard):
            compound >= +0.05  →  positive
            compound <= -0.05  →  challenging
            otherwise          →  neutral
        """
        sia = SentimentIntensityAnalyzer()

        keyword_total: Counter = Counter()
        by_sentiment: dict[str, Counter] = {
            "positive":    Counter(),
            "neutral":     Counter(),
            "challenging": Counter(),
        }
        per_reflection: list[dict] = []

        for entry in reflections:
            text       = entry.get("text", entry.get("reflection_text", ""))
            text_lower = text.lower()

            # VADER-computed sentiment (overrides any pre-label)
            vader_scores = sia.polarity_scores(text)
            compound     = vader_scores["compound"]
            if compound >= 0.05:
                sentiment = "positive"
            elif compound <= -0.05:
                sentiment = "challenging"
            else:
                sentiment = "neutral"

            per_reflection.append({
                "text_preview":       text[:80] + ("…" if len(text) > 80 else ""),
                "vader_compound":     round(compound, 4),
                "sentiment_computed": sentiment,
                "sentiment_original": entry.get("sentiment", entry.get("sentiment_type", "unlabeled")),
            })

            # Keyword matching (unchanged — operates on VADER-classified sentiment bucket)
            for keyword, variants in HAWAIIAN_KEYWORDS.items():
                hits = sum(
                    len(re.findall(r"\b" + re.escape(v) + r"\b", text_lower))
                    for v in variants
                )
                if hits:
                    keyword_total[keyword] += hits
                    by_sentiment.setdefault(sentiment, Counter())[keyword] += hits

        # Build insights
        insights = []
        for keyword, count in keyword_total.most_common(3):
            pos      = by_sentiment["positive"].get(keyword, 0)
            chal     = by_sentiment["challenging"].get(keyword, 0)
            pct_pos  = round(pos / max(count, 1) * 100)
            insights.append(
                f"{keyword} mentioned {count}× — {pct_pos}% in positive context"
            )

        kuleana_pos  = by_sentiment["positive"].get("Kuleana", 0)
        kuleana_chal = by_sentiment["challenging"].get("Kuleana", 0)
        malama_pos   = by_sentiment["positive"].get("Mālama", 0)

        if kuleana_chal > kuleana_pos:
            insights.append(
                "⚠️  Kuleana appears predominantly in challenging contexts — "
                "students may need mentorship around responsibility framing"
            )
        if malama_pos > 0:
            insights.append(
                "✅ Mālama (care/stewardship) is strongly positive — "
                "use land-based activities to reinforce cultural connection"
            )

        return {
            "total_reflections":    len(reflections),
            "keyword_frequencies":  dict(keyword_total.most_common()),
            "by_sentiment": {
                s: dict(c) for s, c in by_sentiment.items()
            },
            "insights":             insights,
            "per_reflection_vader": per_reflection,
        }

    # -----------------------------------------------------------------------
    # PHASE 5 — INTERPRET
    # -----------------------------------------------------------------------

    def interpret(self) -> dict:
        """Generate per-student recommendations and cohort-level narrative."""
        df = self.df_scored
        recommendations = []

        # Per-student recommendations for bottom and top performers
        for _, row in df[df["proficiency"] == "Below"].iterrows():
            rec = {
                "student_key":   row["student_key"],
                "composite_score": row["composite_score"],
                "proficiency":   row["proficiency"],
                "actions": [],
            }
            if not row["is_hawaiian_language"]:
                rec["actions"].append("Enrol in ʻŌlelo Hawaiʻi programme (raises ROOT_IKE base score via cultural immersion)")
            if not row["is_halau_hula"]:
                rec["actions"].append("Connect with Hālau Hula programme (raises ROOT_IKE base score via embodied practice)")
            if not row["is_pbl"]:
                rec["actions"].append("Include in PBL-by-Design cohort (supports LEAF indicators: problem-solving, collaboration)")
            rec["actions"].append("Schedule Kūpuna mentorship sessions")
            recommendations.append(rec)

        for _, row in df[df["proficiency"] == "Advanced"].iterrows():
            recommendations.append({
                "student_key":   row["student_key"],
                "composite_score": row["composite_score"],
                "proficiency":   "Advanced",
                "actions": ["Nominate as cultural peer mentor", "Feature in ʻIke Kūpuna showcase"],
            })

        # Cohort-level narrative
        mean_score  = round(float(df["composite_score"].mean()), 2)
        pct_prof    = round(
            len(df[df["proficiency"].isin(["Advanced", "Proficient"])]) / max(len(df), 1) * 100, 1
        )
        below_count = len(df[df["proficiency"] == "Below"])

        # Programme effectiveness summary
        lang_impact = (
            df[df["is_hawaiian_language"]]["composite_score"].mean()
            - df[~df["is_hawaiian_language"]]["composite_score"].mean()
        )
        hula_impact = (
            df[df["is_halau_hula"]]["composite_score"].mean()
            - df[~df["is_halau_hula"]]["composite_score"].mean()
        )

        narrative = {
            "cohort_mean": mean_score,
            "pct_proficient_or_above": pct_prof,
            "students_needing_support": below_count,
            "hawaiian_language_effect": round(float(lang_impact), 2),
            "halau_hula_effect":        round(float(hula_impact), 2),
            "summary": (
                f"The cohort mean for ʻIke Kūpuna is {mean_score:.1f}. "
                f"{pct_prof}% of students are Proficient or Advanced. "
                f"{below_count} students require targeted cultural support. "
                f"Hawaiian Language programme shows a {lang_impact:+.1f} pt effect; "
                f"Hālau Hula shows a {hula_impact:+.1f} pt effect."
            ),
        }

        return {
            "narrative":        narrative,
            "recommendations":  recommendations,
        }

    # -----------------------------------------------------------------------
    # EXPORT
    # -----------------------------------------------------------------------

    def export(self, path: Path | None = None) -> Path:
        """Write the full report to a JSON file and return the path."""
        out_path = path or (OUTPUT_DIR / "ike_kupuna_analysis.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False, default=str)
        return out_path

    # -----------------------------------------------------------------------
    # RUN — full OSEMN pipeline
    # -----------------------------------------------------------------------

    def run(self, reflections: list[dict] | None = None) -> dict:
        """
        Execute the complete OSEMN pipeline and return the final report.

        Parameters
        ----------
        reflections : list of dicts with keys 'text' and 'sentiment'.
                      Defaults to built-in sample reflections.
        """
        reflections = reflections or SAMPLE_REFLECTIONS

        # O — Obtain
        self.obtain()
        n_raw = len(self.df_raw)

        # S — Scrub
        self.scrub()
        n_clean = len(self.df_clean)

        # E — Explore
        eda = self.explore()

        # M — Model
        self.model()

        # N — iNterpret (incl. NLP)
        self.nlp_results = self._nlp_analyse(reflections)
        interpretation   = self.interpret()

        # Anomaly summary
        critical = sum(1 for a in self.anomalies if a["severity"] == "CRITICAL")
        high     = sum(1 for a in self.anomalies if a["severity"] == "HIGH")
        medium   = sum(1 for a in self.anomalies if a["severity"] == "MEDIUM")
        low      = sum(1 for a in self.anomalies if a["severity"] == "LOW")

        self.report = {
            "meta": {
                "indicator_code": INDICATOR_CODE,
                "indicator_name": INDICATOR_NAME,
                "analysis_timestamp": datetime.now().isoformat(),
                "db_path": str(self.db_path),
                "formula": "Score = 0.70×Base_Score + 0.30×Wellbeing_Score",
                "formula_notes": (
                    "v2: programme_bonus channel removed (was double-counting causal effects "
                    "already encoded in normalized_score). Wellbeing uses raw wb_cultural×0.30. "
                    "Missing wellbeing → weight redistribution: base_w absorbs 0.30 → 1.00 "
                    "(avoids both zero-penalty cap and phantom midpoint imputation). "
                    "scoring_mode field: 'composite' | 'assessment_only'."
                ),
                "weights": WEIGHTS,
                "proficiency_thresholds": PROFICIENCY_THRESHOLDS,
            },
            "data_quality": {
                "records_extracted": n_raw,
                "records_clean":     n_clean,
                "records_removed":   n_raw - n_clean,
                "purity_pct":        round(n_clean / max(n_raw, 1) * 100, 2),
                "anomaly_summary": {
                    "total":    len(self.anomalies),
                    "critical": critical,
                    "high":     high,
                    "medium":   medium,
                    "low":      low,
                },
                "anomaly_detail": self.anomalies,
                "dropped_records_log": self.dropped_records_log,
            },
            "eda": eda,
            "model_output": {
                "scored_students": len(self.df_scored),
                "proficiency_distribution": (
                    self.df_scored["proficiency"].value_counts().to_dict()
                ),
                "score_stats": {
                    "mean":   round(float(self.df_scored["composite_score"].mean()), 2),
                    "std":    round(float(self.df_scored["composite_score"].std()), 2),
                    "min":    round(float(self.df_scored["composite_score"].min()), 2),
                    "max":    round(float(self.df_scored["composite_score"].max()), 2),
                },
                "student_scores": self.df_scored.to_dict(orient="records"),
            },
            "nlp": self.nlp_results,
            "interpretation": interpretation,
        }

        return self.report


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("🔮 Archmage: Awakening 'Ike Kūpuna Analysis Module...")
    print("=" * 72)

    analyzer = IkeKupunaAnalyzer()
    report   = analyzer.run()
    out_path = analyzer.export()

    # ── Summary printout ────────────────────────────────────────────────────
    meta = report["meta"]
    dq   = report["data_quality"]
    eda  = report["eda"]
    mo   = report["model_output"]
    interp = report["interpretation"]

    print(f"\n📍 Indicator : {meta['indicator_name']}")
    print(f"🕐 Timestamp : {meta['analysis_timestamp'][:19]}")
    print(f"\n{'─'*72}")
    print(f"  PHASE 1 — OBTAIN")
    print(f"    Records extracted   : {dq['records_extracted']}")
    print(f"\n  PHASE 2 — SCRUB")
    print(f"    Clean records       : {dq['records_clean']}  ({dq['purity_pct']}%)")
    print(f"    Anomalies detected  : {dq['anomaly_summary']['total']} "
          f"(CRIT:{dq['anomaly_summary']['critical']} "
          f"HIGH:{dq['anomaly_summary']['high']} "
          f"MED:{dq['anomaly_summary']['medium']} "
          f"LOW:{dq['anomaly_summary']['low']})")

    print(f"\n  PHASE 3 — EXPLORE")
    dist = eda["distribution"]
    print(f"    Score  mean / std   : {dist['mean']} / {dist['std']}")
    print(f"    Score  min  / max   : {dist['min']} / {dist['max']}")
    print(f"    Proficiency levels  :")
    for lvl in ["Advanced", "Proficient", "Approaching", "Below"]:
        p = eda["proficiency"][lvl]
        bar = "█" * int(p["pct"] / 3)
        print(f"      {lvl:12s}  {p['count']:3d}  ({p['pct']:5.1f}%)  {bar}")

    print(f"\n    Programme impact    :")
    for prog, d in eda["programme_impact"].items():
        sig = "✅ significant" if d["significant"] else "— not significant"
        print(f"      {prog:20s}  effect={d['effect_size_pts']:+.2f} pts  p={d['p_value']}  {sig}")

    print(f"\n  PHASE 4 — MODEL")
    print(f"    Formula             : {meta['formula']}")
    print(f"    Composite mean      : {mo['score_stats']['mean']}")
    print(f"    Proficiency dist    : ", end="")
    print("  ".join(f"{k}:{v}" for k, v in mo["proficiency_distribution"].items()))

    drl = dq.get("dropped_records_log", {})
    if drl:
        print(f"\n  DROPPED RECORD LOG")
        print(f"    Total dropped       : {drl.get('total_dropped', 0)}  "
              f"(drop rate: {drl.get('drop_rate_pct', 0)}%)")
        for reason in drl.get("reasons", []):
            print(f"    • {reason['type']} — {reason['count']} records: {reason['description']}")
        if not drl.get("reasons"):
            print(f"    No records dropped — 0 critical anomalies.")

    print(f"\n  PHASE 4b — NLP")
    nlp = report["nlp"]
    print(f"    Reflections analysed: {nlp['total_reflections']}")
    print(f"    Top keywords        : ", end="")
    top_kw = list(nlp["keyword_frequencies"].items())[:4]
    print("  ".join(f"{k}:{v}" for k, v in top_kw))
    for insight in nlp["insights"][:3]:
        print(f"    → {insight}")

    print(f"\n  PHASE 5 — INTERPRET")
    narr = interp["narrative"]
    print(f"    {narr['summary']}")
    print(f"    Students needing support : {narr['students_needing_support']}")
    print(f"    Recommendations generated: {len(interp['recommendations'])}")

    print(f"\n{'─'*72}")
    print(f"💾  Report saved → {out_path}")
    print(f"{'='*72}")
    print("✨  'Ike Kūpuna analysis complete. Mana purified and channeled.")
