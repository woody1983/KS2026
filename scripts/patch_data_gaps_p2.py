#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Gap Patch — Phase 2 · Medium & Low Priority Fixes
=======================================================
Author  : The Ironforge Miner (铁炉堡矿工) + The Night's Watch (守夜人)
Purpose : Address remaining data gaps after Phase 1 patch.

Gaps addressed:
  PRE    dim_date               — empty; seed full 2025-26 academic year
  GAP-5  dim_e_ola_indicators   — 6 NULL fields across all 14 indicators
  GAP-7a qualitative_data_id    — link to student_cultural_reflections
  GAP-7b project_key            — seed dim_pbl_projects + link PBL outcomes
  BONUS  fact_pbl_implementation — empty; seed fidelity metrics for PBL students
"""

import sqlite3
import random
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "e_ola_enterprise.db"
SEED = 42
random.seed(SEED)

# ─────────────────────────────────────────────────────────────────────────────
# dim_date seeder  (FK dependency for fact_pbl_implementation)
# ─────────────────────────────────────────────────────────────────────────────

HAWAIIAN_HOLIDAYS = {
    "2025-09-01", "2025-11-11", "2025-11-27", "2025-11-28",
    "2025-12-25", "2026-01-01", "2026-01-19", "2026-02-16",
    "2026-03-26", "2026-05-25", "2026-06-11",
}

ACADEMIC_TERMS = [
    ("2025-08-04", "2025-12-19", "Semester 1"),
    ("2026-01-05", "2026-06-12", "Semester 2"),
]

DAY_NAMES = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
MONTH_NAMES = ["","January","February","March","April","May","June",
               "July","August","September","October","November","December"]


def seed_dim_date(cur, start: date = date(2025, 7, 1), end: date = date(2026, 6, 30)):
    cur.execute("SELECT COUNT(*) FROM dim_date")
    if cur.fetchone()[0] > 0:
        print("  dim_date already seeded — skip")
        return 0

    rows = []
    d = start
    while d <= end:
        ds = d.isoformat()
        is_holiday = ds in HAWAIIAN_HOLIDAYS
        is_school = (
            d.weekday() < 5
            and not is_holiday
            and (
                "2025-08-04" <= ds <= "2025-12-19"
                or "2026-01-05" <= ds <= "2026-06-12"
            )
        )
        fiscal_year = f"{d.year}-{d.year+1}" if d.month >= 7 else f"{d.year-1}-{d.year}"
        acad_year = "2025-26"
        acad_term, ts, te = "Summer Break", "", ""
        for s, e, name in ACADEMIC_TERMS:
            if s <= ds <= e:
                acad_term, ts, te = name, s, e
                break
        rows.append((
            int(d.strftime("%Y%m%d")), ds,
            d.weekday() + 1, DAY_NAMES[d.weekday()],
            d.day, d.timetuple().tm_yday,
            d.isocalendar()[1], d.month, MONTH_NAMES[d.month],
            (d.month - 1) // 3 + 1, d.year,
            fiscal_year, acad_year, acad_term, ts, te,
            1 if is_school else 0,
            1 if is_holiday else 0,
            "Holiday" if is_holiday else "",
        ))
        d += timedelta(days=1)

    cur.executemany(
        """INSERT OR IGNORE INTO dim_date
           (date_key, full_date, day_of_week, day_name, day_of_month,
            day_of_year, week_of_year, month_number, month_name, quarter,
            year_number, fiscal_year, academic_year, academic_term,
            term_start_date, term_end_date, is_school_day, is_holiday,
            holiday_name)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows,
    )
    print(f"  dim_date: {len(rows)} rows inserted (2025-07-01 → 2026-06-30)")
    return len(rows)


# ─────────────────────────────────────────────────────────────────────────────
# GAP-5 Indicator metadata
# ─────────────────────────────────────────────────────────────────────────────

INDICATOR_META = {
    "ROOT_IKE": {
        "data_collection_method": "Self-report survey, teacher observation, portfolio review",
        "assessment_frequency": "Semester",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 75,
        "learning_outcomes": (
            "Student demonstrates knowledge of Hawaiian history, protocol, and traditional "
            "practices; applies ancestral wisdom in daily decision-making; articulates cultural "
            "identity through language and values"
        ),
    },
    "ROOT_ALOHA": {
        "data_collection_method": "Portfolio review, experiential observation, teacher assessment",
        "assessment_frequency": "Semester",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 75,
        "learning_outcomes": (
            "Student demonstrates emotional connection to Hawaiian land; practices environmental "
            "stewardship; participates in ʻāina-based learning experiences; articulates "
            "responsibility to the natural world"
        ),
    },
    "ROOT_KUPONO": {
        "data_collection_method": "Behavioral observation, peer 360, teacher narrative assessment",
        "assessment_frequency": "Semester",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 70,
        "learning_outcomes": (
            "Student demonstrates honesty and fairness in academic and community settings; upholds "
            "Kamehameha Schools values; reflects on ethical decision-making; models pono behavior "
            "for peers"
        ),
    },
    "TRUNK_MALAMA": {
        "data_collection_method": "Behavioral records, SIS participation data, teacher observation",
        "assessment_frequency": "Quarterly",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 75,
        "learning_outcomes": (
            "Student actively cares for school community and environment; fulfills assigned "
            "kuleana (responsibilities); demonstrates servant leadership through consistent "
            "action; mentors younger students"
        ),
    },
    "TRUNK_ALAKAI": {
        "data_collection_method": "Portfolio review, teacher narrative, peer 360 assessment",
        "assessment_frequency": "Semester",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 70,
        "learning_outcomes": (
            "Student leads with cultural integrity and service orientation; facilitates group "
            "decision-making; demonstrates alakaʻi (leadership) qualities; organizes and "
            "motivates peers toward shared goals"
        ),
    },
    "TRUNK_KULIA": {
        "data_collection_method": "Standardized assessment, portfolio, self-report survey",
        "assessment_frequency": "Semester",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 75,
        "learning_outcomes": (
            "Student strives for excellence in academic and cultural pursuits; persists through "
            "challenge; sets and monitors personal growth goals; demonstrates continuous "
            "improvement across all E Ola! domains"
        ),
    },
    "LEAF_ACAD": {
        "data_collection_method": "Standardized test, GPA, course assessment records",
        "assessment_frequency": "Quarterly",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 80,
        "learning_outcomes": (
            "Student meets or exceeds grade-level standards in core subjects; demonstrates "
            "mastery of Hawaiʻi State learning standards; applies academic skills to "
            "real-world Hawaiian contexts; shows consistent academic growth"
        ),
    },
    "LEAF_MINDSET": {
        "data_collection_method": "Self-report survey, teacher observation, NLP journal analysis",
        "assessment_frequency": "Semester",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 70,
        "learning_outcomes": (
            "Student embraces challenge as a learning opportunity; responds to failure with "
            "productive strategies; demonstrates belief in ability to grow through effort; "
            "uses growth language in reflections and discussions"
        ),
    },
    "LEAF_EFFICACY": {
        "data_collection_method": "Self-report survey, teacher observation",
        "assessment_frequency": "Semester",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 70,
        "learning_outcomes": (
            "Student expresses confidence in ability to succeed; initiates learning tasks "
            "independently; sets realistic yet ambitious goals; attributes outcomes to effort "
            "and strategy rather than fixed ability"
        ),
    },
    "LEAF_PROBLEM": {
        "data_collection_method": "PBL-by-Design rubric, portfolio, peer assessment",
        "assessment_frequency": "Project-cycle",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 75,
        "learning_outcomes": (
            "Student defines problems clearly; generates multiple solution strategies; evaluates "
            "solutions using evidence; iterates based on feedback; applies problem-solving to "
            "Hawaiian community challenges"
        ),
    },
    "LEAF_INNOV": {
        "data_collection_method": "PBL-by-Design rubric, portfolio review, teacher observation",
        "assessment_frequency": "Project-cycle",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 70,
        "learning_outcomes": (
            "Student generates novel ideas with cultural grounding; experiments with creative "
            "approaches; combines traditional Hawaiian knowledge with contemporary solutions; "
            "demonstrates design thinking across disciplines"
        ),
    },
    "LEAF_COLLAB": {
        "data_collection_method": "Peer 360 assessment, teacher observation, PBL team metrics",
        "assessment_frequency": "Project-cycle",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 75,
        "learning_outcomes": (
            "Student contributes meaningfully to group work; communicates effectively across "
            "cultural and academic contexts; resolves conflict constructively; practices the "
            "Hawaiian value of working together (laulima)"
        ),
    },
    "LEAF_GLOBAL": {
        "data_collection_method": "Portfolio review, self-report survey, teacher assessment",
        "assessment_frequency": "Annual",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 70,
        "learning_outcomes": (
            "Student connects Hawaiian identity to global contexts; demonstrates awareness of "
            "diverse perspectives; engages with intercultural exchange; articulates Hawaiian "
            "contributions to global discourse on sustainability and indigenous rights"
        ),
    },
    "FRUIT_WELLBEING": {
        "data_collection_method": "Self-report survey, behavioral records, teacher observation",
        "assessment_frequency": "Semester",
        "min_score": 0, "max_score": 100, "proficiency_threshold": 65,
        "learning_outcomes": (
            "Student demonstrates holistic well-being across cultural, spiritual, social, "
            "economic, physical, emotional, and cognitive dimensions; lives in alignment with "
            "E Ola! values; supports the well-being of family and community"
        ),
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# PBL Projects (10 realistic Kamehameha Schools projects)
# ─────────────────────────────────────────────────────────────────────────────

PBL_PROJECTS = [
    {
        "project_code": "PBL-2025-001",
        "project_title": "Ahupuaʻa Restoration Initiative",
        "project_description": "Students design and implement a watershed restoration plan for a degraded ahupuaʻa section, applying traditional Hawaiian land management knowledge alongside modern environmental science.",
        "project_start_date": "2025-08-25", "project_end_date": "2025-12-15",
        "academic_year": "2025-26", "academic_term": "Semester 1",
        "subject_area": "Environmental Science / Hawaiian Studies",
        "grade_levels": "9-10", "project_type": "Community Service",
        "primary_indicator_key": 2, "secondary_indicators": "1,4,10,11",
        "implementation_phase": "Complete", "teacher_id": "T-001",
    },
    {
        "project_code": "PBL-2025-002",
        "project_title": "Moʻolelo Digital Archive",
        "project_description": "Students interview kūpuna and create a bilingual Hawaiian/English digital archive of traditional stories, preserving ancestral wisdom for future generations through modern media tools.",
        "project_start_date": "2025-08-25", "project_end_date": "2025-12-15",
        "academic_year": "2025-26", "academic_term": "Semester 1",
        "subject_area": "Language Arts / Hawaiian Language",
        "grade_levels": "7-8", "project_type": "Research & Documentation",
        "primary_indicator_key": 1, "secondary_indicators": "2,5,12",
        "implementation_phase": "Complete", "teacher_id": "T-002",
    },
    {
        "project_code": "PBL-2025-003",
        "project_title": "Community Food Forest",
        "project_description": "Students design and plant a native Hawaiian food forest using traditional mala cultivation techniques, creating a living laboratory that feeds the school community and demonstrates ahupuaʻa principles.",
        "project_start_date": "2025-09-08", "project_end_date": "2026-05-29",
        "academic_year": "2025-26", "academic_term": "Full Year",
        "subject_area": "Agriculture / Biology",
        "grade_levels": "6-8", "project_type": "Yearlong Community Project",
        "primary_indicator_key": 4, "secondary_indicators": "2,10,12",
        "implementation_phase": "In Progress", "teacher_id": "T-003",
    },
    {
        "project_code": "PBL-2025-004",
        "project_title": "Youth Leadership Summit",
        "project_description": "Student leaders plan, facilitate, and evaluate a campus-wide summit on Hawaiian values in modern leadership, hosting guest speakers, workshops, and a public showcase of E Ola! student projects.",
        "project_start_date": "2025-10-01", "project_end_date": "2025-11-14",
        "academic_year": "2025-26", "academic_term": "Semester 1",
        "subject_area": "Leadership / Social Studies",
        "grade_levels": "10-12", "project_type": "Event Leadership",
        "primary_indicator_key": 5, "secondary_indicators": "3,12,13",
        "implementation_phase": "Complete", "teacher_id": "T-004",
    },
    {
        "project_code": "PBL-2025-005",
        "project_title": "Marine Protected Area Data Dashboard",
        "project_description": "Students collect, analyze, and visualize reef health data for a local marine protected area, presenting findings to the State DLNR and community groups in both Hawaiian and English.",
        "project_start_date": "2025-09-15", "project_end_date": "2026-01-30",
        "academic_year": "2025-26", "academic_term": "Semester 1-2 Bridge",
        "subject_area": "Marine Science / Data Science",
        "grade_levels": "11-12", "project_type": "Research & Advocacy",
        "primary_indicator_key": 10, "secondary_indicators": "2,7,11,13",
        "implementation_phase": "Complete", "teacher_id": "T-005",
    },
    {
        "project_code": "PBL-2026-001",
        "project_title": "Lāʻau Hawaiʻi Medicinal Garden",
        "project_description": "Students research traditional Hawaiian plant medicine (lāʻau lapaʻau), cultivate a medicinal garden, and produce educational materials for the school clinic and community health fairs.",
        "project_start_date": "2026-01-12", "project_end_date": "2026-04-24",
        "academic_year": "2025-26", "academic_term": "Semester 2",
        "subject_area": "Biology / Hawaiian Studies",
        "grade_levels": "9-10", "project_type": "Community Health",
        "primary_indicator_key": 1, "secondary_indicators": "2,4,11",
        "implementation_phase": "In Progress", "teacher_id": "T-001",
    },
    {
        "project_code": "PBL-2026-002",
        "project_title": "Innovation Challenge: Ocean Plastic Solutions",
        "project_description": "Teams apply design thinking to develop scalable solutions to ocean plastic pollution affecting Hawaiian reefs and fishing communities, presenting prototypes to a panel of industry and community judges.",
        "project_start_date": "2026-01-26", "project_end_date": "2026-05-08",
        "academic_year": "2025-26", "academic_term": "Semester 2",
        "subject_area": "Engineering / Environmental Science",
        "grade_levels": "10-12", "project_type": "Design Challenge",
        "primary_indicator_key": 11, "secondary_indicators": "10,12,13",
        "implementation_phase": "In Progress", "teacher_id": "T-005",
    },
    {
        "project_code": "PBL-2026-003",
        "project_title": "ʻŌlelo Hawaiʻi Revitalization Media Campaign",
        "project_description": "Students produce a multi-platform media campaign promoting Hawaiian language use among youth, partnering with local radio stations and community organizations.",
        "project_start_date": "2026-02-02", "project_end_date": "2026-05-29",
        "academic_year": "2025-26", "academic_term": "Semester 2",
        "subject_area": "Hawaiian Language / Communications",
        "grade_levels": "8-10", "project_type": "Media & Advocacy",
        "primary_indicator_key": 1, "secondary_indicators": "5,11,12,13",
        "implementation_phase": "In Progress", "teacher_id": "T-002",
    },
    {
        "project_code": "PBL-2026-004",
        "project_title": "Hālau Hula — Community Performance & Curriculum",
        "project_description": "Advanced hula students choreograph original hula interpreting E Ola! values, perform at community events, and develop a beginner curriculum for elementary school outreach visits.",
        "project_start_date": "2026-01-12", "project_end_date": "2026-06-05",
        "academic_year": "2025-26", "academic_term": "Semester 2",
        "subject_area": "Hawaiian Dance / Cultural Arts",
        "grade_levels": "9-12", "project_type": "Cultural Performance",
        "primary_indicator_key": 3, "secondary_indicators": "1,2,5,12",
        "implementation_phase": "In Progress", "teacher_id": "T-006",
    },
    {
        "project_code": "PBL-2026-005",
        "project_title": "Junior Achievement: Kaʻana Like Business Pitch",
        "project_description": "Students develop and pitch culturally-grounded business concepts that serve the Hawaiian community, applying traditional values of kaʻana like (sharing) and mālama to modern entrepreneurship.",
        "project_start_date": "2026-02-16", "project_end_date": "2026-05-22",
        "academic_year": "2025-26", "academic_term": "Semester 2",
        "subject_area": "Business / Economics",
        "grade_levels": "11-12", "project_type": "Entrepreneurship",
        "primary_indicator_key": 6, "secondary_indicators": "7,10,11,12,13",
        "implementation_phase": "In Progress", "teacher_id": "T-004",
    },
]

# PBL-relevant indicator keys (where project_key should be non-NULL)
PBL_INDICATOR_KEYS = {1, 2, 3, 4, 5, 10, 11, 12}

# Indicators that have qualitative component (Roots + Trunk + Wellbeing)
QUALITATIVE_INDICATORS = {1, 2, 3, 4, 5, 6, 14}

# PBL implementation metrics
PBL_METRICS = [
    ("Engagement",    "participation_rate",  "%",   60.0, 100.0),
    ("Engagement",    "attendance_score",    "pts", 70.0, 100.0),
    ("Quality",       "rubric_score",        "pts", 55.0, 100.0),
    ("Quality",       "peer_review_score",   "pts", 60.0, 100.0),
    ("Fidelity",      "design_fidelity",     "pts", 65.0, 100.0),
    ("Collaboration", "team_contribution",   "pts", 60.0, 100.0),
]


def fidelity_level(score: float) -> str:
    if score >= 88:  return "Exceeding"
    if score >= 75:  return "Meeting"
    if score >= 60:  return "Approaching"
    return "Developing"


def rand_score(lo: float, hi: float, bias: float = 0.0) -> float:
    mid = (lo + hi) / 2 + bias
    sd  = (hi - lo) / 5
    v   = random.gauss(mid, sd)
    return round(max(lo, min(hi, v)), 1)


def nearest_school_day(d: date, school_days: set) -> int:
    """Return date_key of nearest school day on or after d."""
    for i in range(30):
        candidate = d + timedelta(days=i)
        dk = int(candidate.strftime("%Y%m%d"))
        if dk in school_days:
            return dk
    # fallback: any existing date_key
    return int(d.strftime("%Y%m%d"))


# ─────────────────────────────────────────────────────────────────────────────
# Main patch function
# ─────────────────────────────────────────────────────────────────────────────

def patch(db_path: Path = DB_PATH):
    conn = sqlite3.connect(db_path)
    # Keep FK off for this script — dim_date may be empty when outcomes were seeded,
    # and we want UPDATE statements to remain unrestricted.
    conn.execute("PRAGMA foreign_keys = OFF")
    cur  = conn.cursor()
    results = {}

    # ── PRE: dim_date ─────────────────────────────────────────────────────────
    print("\n[PRE] Seeding dim_date for 2025-26 academic year...")
    n_dates = seed_dim_date(cur)
    conn.commit()

    # Build set of valid date_keys for school days
    cur.execute("SELECT date_key FROM dim_date WHERE is_school_day = 1")
    school_day_keys = {r[0] for r in cur.fetchall()}

    # ── GAP-5: dim_e_ola_indicators missing fields ────────────────────────────
    print("\n[GAP-5] Filling dim_e_ola_indicators missing fields...")
    cur.execute("SELECT COUNT(*) FROM dim_e_ola_indicators WHERE learning_outcomes IS NULL")
    gap5_remaining = cur.fetchone()[0]

    if gap5_remaining == 0:
        print("  (already complete — skip)")
        results["gap5_indicators_updated"] = 0
    else:
        updated = 0
        for code, meta in INDICATOR_META.items():
            cur.execute(
                """UPDATE dim_e_ola_indicators
                   SET data_collection_method = ?,
                       assessment_frequency   = ?,
                       min_score              = ?,
                       max_score              = ?,
                       proficiency_threshold  = ?,
                       learning_outcomes      = ?,
                       updated_at             = datetime('now')
                   WHERE indicator_code = ?""",
                (
                    meta["data_collection_method"],
                    meta["assessment_frequency"],
                    meta["min_score"], meta["max_score"],
                    meta["proficiency_threshold"],
                    meta["learning_outcomes"],
                    code,
                ),
            )
            updated += cur.rowcount
        conn.commit()
        print(f"  ✅  {updated} indicators updated")
        results["gap5_indicators_updated"] = updated

    # ── GAP-7b: Seed dim_pbl_projects ────────────────────────────────────────
    print("\n[GAP-7b] Seeding dim_pbl_projects (10 projects)...")
    cur.execute("SELECT COUNT(*) FROM dim_pbl_projects")
    pbl_count = cur.fetchone()[0]

    if pbl_count > 0:
        print(f"  (already {pbl_count} projects — skip insert)")
        results["gap7b_projects_inserted"] = 0
    else:
        for p in PBL_PROJECTS:
            cur.execute(
                """INSERT INTO dim_pbl_projects
                   (project_code, project_title, project_description,
                    project_start_date, project_end_date, academic_year,
                    academic_term, subject_area, grade_levels, project_type,
                    primary_indicator_key, secondary_indicators,
                    implementation_phase, teacher_id, is_active)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)""",
                (
                    p["project_code"], p["project_title"], p["project_description"],
                    p["project_start_date"], p["project_end_date"], p["academic_year"],
                    p["academic_term"], p["subject_area"], p["grade_levels"],
                    p["project_type"], p["primary_indicator_key"],
                    p["secondary_indicators"], p["implementation_phase"],
                    p["teacher_id"],
                ),
            )
        conn.commit()
        print(f"  ✅  {len(PBL_PROJECTS)} projects inserted")
        results["gap7b_projects_inserted"] = len(PBL_PROJECTS)

    # Load project info for downstream use
    cur.execute(
        "SELECT project_key, primary_indicator_key, secondary_indicators, "
        "project_start_date, project_end_date FROM dim_pbl_projects"
    )
    proj_rows = cur.fetchall()
    proj_dates = {pk: (sd, ed) for pk, pi, si, sd, ed in proj_rows}
    proj_indicators = [(pk, pi, si) for pk, pi, si, sd, ed in proj_rows]

    # ── GAP-7b: Link project_key on relevant outcomes ─────────────────────────
    print("\n[GAP-7b] Linking project_key on fact_e_ola_outcomes...")
    cur.execute("SELECT COUNT(*) FROM fact_e_ola_outcomes WHERE project_key IS NOT NULL")
    already_linked = cur.fetchone()[0]
    if already_linked > 0:
        print(f"  (already {already_linked} rows linked — skip)")
        results["gap7b_outcomes_linked"] = 0
    else:
        cur.execute(
            "SELECT student_key FROM dim_students_masked WHERE is_pbl_participant = 1 AND is_current = 1"
        )
        pbl_students = [r[0] for r in cur.fetchall()]

        linked = 0
        for sk in pbl_students:
            assigned = random.sample(proj_indicators, min(3, len(proj_indicators)))
            for proj_key, primary_ind, sec_inds_str in assigned:
                ind_keys = {primary_ind}
                if sec_inds_str:
                    for part in sec_inds_str.split(","):
                        try:
                            ind_keys.add(int(part.strip()))
                        except ValueError:
                            pass
                ind_keys &= PBL_INDICATOR_KEYS

                for ind_key in ind_keys:
                    cur.execute(
                        """UPDATE fact_e_ola_outcomes
                           SET project_key = ?
                           WHERE student_key = ? AND indicator_key = ?
                             AND project_key IS NULL""",
                        (proj_key, sk, ind_key),
                    )
                    linked += cur.rowcount

        conn.commit()
        print(f"  ✅  {linked} outcome rows linked to a project")
        results["gap7b_outcomes_linked"] = linked

    # ── GAP-7a: Link qualitative_data_id → student_cultural_reflections ───────
    print("\n[GAP-7a] Linking qualitative_data_id on cultural/qualitative outcomes...")
    cur.execute("SELECT COUNT(*) FROM fact_e_ola_outcomes WHERE qualitative_data_id IS NOT NULL")
    already_qual = cur.fetchone()[0]
    if already_qual > 0:
        print(f"  (already {already_qual} rows linked — skip)")
        results["gap7a_qual_linked"] = 0
    else:
        cur.execute(
            "SELECT student_key, reflection_id FROM student_cultural_reflections "
            "ORDER BY student_key, reflection_id"
        )
        student_reflections: dict[int, list[int]] = {}
        for sk, rid in cur.fetchall():
            student_reflections.setdefault(sk, []).append(rid)

        linked_qual = 0
        for sk, rids in student_reflections.items():
            cycle = (rids * 10)  # enough to cover all qualitative indicators
            for i, ind_key in enumerate(sorted(QUALITATIVE_INDICATORS)):
                rid = cycle[i % len(rids)]
                cur.execute(
                    """UPDATE fact_e_ola_outcomes
                       SET qualitative_data_id = ?
                       WHERE student_key = ? AND indicator_key = ?
                         AND qualitative_data_id IS NULL""",
                    (rid, sk, ind_key),
                )
                linked_qual += cur.rowcount

        conn.commit()
        print(f"  ✅  {linked_qual} outcome rows linked to a reflection")
        results["gap7a_qual_linked"] = linked_qual

    # ── BONUS: Seed fact_pbl_implementation ───────────────────────────────────
    print("\n[BONUS] Seeding fact_pbl_implementation for PBL participants...")
    cur.execute("SELECT COUNT(*) FROM fact_pbl_implementation")
    if cur.fetchone()[0] > 0:
        print("  (already seeded — skip)")
        results["bonus_pbl_impl_inserted"] = 0
    else:
        cur.execute(
            """SELECT s.student_key, s.grade_level,
                      s.is_hawaiian_language, s.is_hālau_hula
               FROM dim_students_masked s
               WHERE s.is_pbl_participant = 1 AND s.is_current = 1"""
        )
        pbl_students_data = cur.fetchall()

        impl_rows = 0
        BATCH_ID = "PATCH_GAP_BONUS_20260225"

        for sk, grade, is_lang, is_hula in pbl_students_data:
            cultural_bias = (3 if is_lang else 0) + (2 if is_hula else 0)
            assigned = random.sample(list(proj_dates.keys()), min(2, len(proj_dates)))

            for proj_key in assigned:
                start_str, end_str = proj_dates[proj_key]
                start = date.fromisoformat(start_str)
                end   = date.fromisoformat(end_str)
                mid   = start + (end - start) // 2
                # Find nearest valid school-day date_key
                dk = nearest_school_day(mid, school_day_keys)

                for metric_cat, metric_name, unit, lo, hi in PBL_METRICS:
                    v = rand_score(lo, hi, cultural_bias)
                    cur.execute(
                        """INSERT INTO fact_pbl_implementation
                           (project_key, student_key, date_key, metric_category,
                            metric_name, metric_value, metric_unit,
                            fidelity_score, fidelity_level, etl_batch_id)
                           VALUES (?,?,?,?,?,?,?,?,?,?)""",
                        (
                            proj_key, sk, dk, metric_cat,
                            metric_name, v, unit,
                            v, fidelity_level(v), BATCH_ID,
                        ),
                    )
                    impl_rows += 1

        conn.commit()
        print(f"  ✅  {impl_rows} PBL implementation rows inserted")
        results["bonus_pbl_impl_inserted"] = impl_rows

    # ── Verification ──────────────────────────────────────────────────────────
    print("\n── Verification ────────────────────────────────────────────────────")

    checks = [
        ("dim_date rows",                           "SELECT COUNT(*) FROM dim_date"),
        ("dim_e_ola_indicators.learning_outcomes NULL", "SELECT COUNT(*) FROM dim_e_ola_indicators WHERE learning_outcomes IS NULL"),
        ("dim_e_ola_indicators.data_collection NULL",   "SELECT COUNT(*) FROM dim_e_ola_indicators WHERE data_collection_method IS NULL"),
        ("dim_pbl_projects total",                  "SELECT COUNT(*) FROM dim_pbl_projects"),
        ("fact_e_ola_outcomes with project_key",    "SELECT COUNT(*) FROM fact_e_ola_outcomes WHERE project_key IS NOT NULL"),
        ("fact_e_ola_outcomes with qual_data_id",   "SELECT COUNT(*) FROM fact_e_ola_outcomes WHERE qualitative_data_id IS NOT NULL"),
        ("fact_pbl_implementation total",           "SELECT COUNT(*) FROM fact_pbl_implementation"),
    ]
    for label, sql in checks:
        cur.execute(sql)
        print(f"  {label:45s}: {cur.fetchone()[0]}")

    print("\n  PBL fidelity distribution:")
    cur.execute(
        "SELECT fidelity_level, COUNT(*) FROM fact_pbl_implementation "
        "GROUP BY fidelity_level ORDER BY COUNT(*) DESC"
    )
    for row in cur.fetchall():
        print(f"    {row[0]:12s}  n={row[1]}")

    conn.close()
    results["status"] = "COMPLETE"
    return results


if __name__ == "__main__":
    print("=" * 68)
    print("  Data Gap Patch — Phase 2 Medium & Low Priority Fixes")
    print("=" * 68)
    res = patch()
    print("\n" + "=" * 68)
    print("  Summary")
    print("=" * 68)
    for k, v in res.items():
        print(f"  {k}: {v}")
    print("\n✅  All remaining gaps patched. The Wall holds.")
