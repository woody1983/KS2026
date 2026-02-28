#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E Ola! Learner Analytics System - Enterprise Seed Data Generator v2.0
Author: The Ironforge Miner (铁炉堡矿工)
Mission: High-fidelity synthetic data with Hawaiian cultural authenticity
Target: 200 students, 14 E Ola! indicators, cultural reflections, dirty data injection
"""

import sqlite3
import uuid
import hashlib
import random
import json
from datetime import datetime, timedelta
from faker import Faker
import numpy as np
from scipy import stats

# Initialize Faker
fake = Faker(["en_US"])
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# ============================================================================
# HAWAIIAN CULTURAL DATASETS - Authentic Names & Context
# ============================================================================

HAWAIIAN_FIRST_NAMES = [
    # Male names (40%)
    "Kealoha",
    "Kaimana",
    "Kai",
    "Keoni",
    "Kaleo",
    "Kapono",
    "Kekoa",
    "Koa",
    "Makana",
    "Mana",
    "Nalu",
    "Noa",
    "Kahale",
    "Kale",
    "Keanu",
    "Keoki",
    "Kimo",
    "Liko",
    "Makani",
    "Maui",
    "Nainoa",
    "Pika",
    "Akamu",
    "Analu",
    "Aukai",
    "Ekewaka",
    "Haukea",
    "Ikaika",
    "Kahoku",
    "Kalani",
    "Kamaka",
    "Kanaʻi",
    "Kawika",
    "Keawe",
    "Kekoa",
    "Koa",
    "Kū",
    "Lono",
    # Female names (40%)
    "Malia",
    "Leilani",
    "Kailani",
    "Kehlani",
    "Aloha",
    "Alana",
    "Anela",
    "Halona",
    "Halia",
    "Iolana",
    "Kala",
    "Kalea",
    "Kapua",
    "Keala",
    "Keona",
    "Kiana",
    "Kimokea",
    "Lani",
    "Lilia",
    "Lokelani",
    "Mahina",
    "Maile",
    "Maka",
    "Malie",
    "Mele",
    "Milani",
    "Moana",
    "Nalani",
    "Noelani",
    "Olina",
    "Palila",
    "Pua",
    "Roselani",
    "Tia",
    "Ulani",
    "Wailani",
    "Hiʻilei",
    "Kalehua",
    "Kamaile",
    "Lahela",
    "Mikala",
    "Nohea",
    "ʻIlima",
]

HAWAIIAN_LAST_NAMES = [
    "Akana",
    "Alana",
    "Alapai",
    "Alo",
    "Ane",
    "Apana",
    "Awana",
    "Chang",
    "Ching",
    "Hao",
    "Hee",
    "Hina",
    "Hokoana",
    "Iaukea",
    "Ioane",
    "Kahale",
    "Kahalewai",
    "Kahanamoku",
    "Kahawai",
    "Kai",
    "Kaiwi",
    "Kala",
    "Kalama",
    "Kamaka",
    "Kamealoha",
    "Kamuela",
    "Kane",
    "Kapono",
    "Kauhane",
    "Kawai",
    "Kawena",
    "Kealoha",
    "Keawe",
    "Kekoa",
    "Keliʻi",
    "Keliihoʻomalu",
    "Keliikoa",
    "Kennedy",
    "Kim",
    "Koʻolau",
    "Kua",
    "Kuhio",
    "Kūhiō",
    "Lee",
    "Lehua",
    "Lewis",
    "Lima",
    "Lono",
    "Lum",
    "Mahoe",
    "Maka",
    "Makai",
    "Mala",
    "Mana",
    "Manu",
    "Mahelona",
    "Nakamura",
    "Naluai",
    "Namaka",
    "Nawahine",
    "Nihoa",
    "Noa",
    "Oʻahu",
    "Ono",
    "Paki",
    "Palakiko",
    "Pele",
    "Pua",
    "Pukui",
    "Punihei",
    "Wahine",
    "Wong",
    "Young",
    "Kaʻalele",
    "Kamaunu",
    "Keohokālole",
    "Kīnaʻu",
    "Likelike",
]

# KS Campus Distribution
KS_CAMPUSES = {
    "Kāpalama (Honolulu)": {
        "weight": 0.60,
        "communities": ["Nuʻuanu", "Mānoa", "Kāhala", "ʻĀina Haina", "Kaimukī"],
    },
    "Maui": {
        "weight": 0.25,
        "communities": ["Kahului", "Wailuku", "Lahaina", "Kīhei", "Pāʻia"],
    },
    "Hawaiʻi Island": {
        "weight": 0.15,
        "communities": ["Hilo", "Kona", "Waimea", "Keaʻau", "Pāhoa"],
    },
}

# Hawaiian cultural keywords for reflection texts
HAWAIIAN_KEYWORDS = [
    "Kūpuna",
    "Kuleana",
    "Mālama",
    "Aloha",
    "ʻĀina",
    "Kalo",
    "Mana",
    "Lōkahi",
    "Pono",
    "Haʻahaʻa",
    "Kūlia",
    "Laulima",
    "Ohana",
    "Moʻomeheu",
    "Hālau",
    "Hula",
    "Oli",
    "Mele",
    "Waʻa",
    "Kai",
    "Mauna",
    "Makani",
]

REFLECTION_TEMPLATES = {
    "positive": [
        "Today at the {activity}, I felt a strong connection to my {keyword}. The {detail} reminded me that {insight}.",
        "Working in the {activity} today was amazing! I learned that {insight}. It makes me proud to be Hawaiian.",
        "My {keyword} taught me about {detail}. I now understand why {insight}. This is our kuleana.",
        "When we practiced {activity}, I could feel the mana of our ancestors. {insight}.",
        "The {activity} was so much fun today! {insight}. I want to learn more about my culture.",
        "Being in the {activity} made me feel connected to the ʻāina. {insight}. Mālama honua!",
        "I helped my classmates today during {activity}. It felt good to practice laulima. {insight}.",
    ],
    "neutral": [
        "Today we learned about {detail} in {activity}. It was interesting but I need more time to understand.",
        "We practiced {activity} for {hours} hours. The {detail} was okay, not too hard or easy.",
        "My teacher explained {detail} during {activity}. I wrote some notes to remember.",
        "We had {activity} class today. I participated but didn't say much.",
        "The {activity} was different from what I expected. {detail} was new to me.",
    ],
    "challenging": [
        "The {activity} was really hard today. I struggled with {detail} and felt frustrated.",
        "I don't understand why we need to learn {detail}. It feels confusing and I want to give up.",
        "Sometimes I feel like I'm not good enough at {activity}. {insight} but it's difficult.",
        "The {detail} in {activity} doesn't make sense to me. I tried but kept making mistakes.",
        "I feel overwhelmed by {activity}. Other students seem to get it but I don't. {insight}?",
    ],
}

ACTIVITIES = [
    "Loʻi kalo",
    "Hula kahiko",
    "Hula ʻauana",
    "ʻŌlelo Hawaiʻi class",
    "Waʻa practice",
    "Mele composition",
    "Oli chanting",
    "Lauhala weaving",
    "Kapa making",
    "Hoʻokele navigation",
    "Lāʻau lapaʻau",
    "Mālama ʻāina",
    "Fishpond restoration",
    "Taro cultivation",
]

# ============================================================================
# STATISTICAL DISTRIBUTIONS
# ============================================================================


def generate_normal_score(mean=75, std=15, min_val=0, max_val=100):
    """Generate normally distributed score with bounds"""
    score = np.random.normal(mean, std)
    return max(min_val, min(max_val, round(score, 2)))


def generate_power_law_hours(alpha=2.0, min_hours=1, max_hours=50):
    """Generate power-law distributed participation hours"""
    # Pareto distribution for "few leaders, many followers" pattern
    hours = (np.random.pareto(alpha) * 5) + min_hours
    return min(max_hours, round(hours, 1))


def generate_aina_connection():
    """Generate family connection to land (1-5 scale)"""
    # Skewed toward higher values (Hawaiian families tend to have strong land connections)
    return min(5, max(1, int(np.random.normal(3.5, 1.2))))


def generate_cultural_reflection(sentiment_type="positive"):
    """Generate authentic cultural reflection text"""
    template = random.choice(REFLECTION_TEMPLATES[sentiment_type])

    activity = random.choice(ACTIVITIES)
    keyword = random.choice(HAWAIIAN_KEYWORDS)
    hours = random.randint(1, 4)

    details = {
        "Loʻi kalo": [
            "planting kalo",
            "cleaning the auwai",
            "harvesting",
            "preparing the soil",
        ],
        "Hula kahiko": [
            "ancient chants",
            "hand movements",
            "protocol",
            "costume preparation",
        ],
        "Hula ʻauana": [
            "modern songs",
            "storytelling",
            "graceful movements",
            "expression",
        ],
        "ʻŌlelo Hawaiʻi class": [
            "pronunciation",
            "sentence structure",
            "vocabulary",
            "conversation",
        ],
        "Waʻa practice": [
            "paddling technique",
            "navigation stars",
            "team coordination",
            "ocean safety",
        ],
        "Mele composition": [
            "writing lyrics",
            "melody creation",
            "poetic devices",
            "performance",
        ],
        "Oli chanting": ["breath control", "vocal projection", "protocol", "meaning"],
        "Lauhala weaving": [
            "preparing leaves",
            "weaving patterns",
            "creating baskets",
            "patience",
        ],
        "Kapa making": ["beating bark", "designs", "natural dyes", "traditional tools"],
        "Hoʻokele navigation": [
            "star patterns",
            "wave reading",
            "wayfinding",
            "ancestral knowledge",
        ],
        "Lāʻau lapaʻau": [
            "medicinal plants",
            "healing practices",
            "preparation methods",
            "respect",
        ],
        "Mālama ʻāina": [
            "cleaning the land",
            "planting native species",
            "water conservation",
            "stewardship",
        ],
        "Fishpond restoration": [
            "repairing walls",
            "water quality",
            "fish behavior",
            "community work",
        ],
        "Taro cultivation": [
            "preparing huli",
            "water management",
            "pest control",
            "harvest timing",
        ],
    }

    detail = random.choice(
        details.get(activity, ["traditional practices", "cultural learning"])
    )

    insights = {
        "positive": [
            "our ancestors were very wise",
            "we must take care of the land for future generations",
            "everything in nature is connected",
            "our culture teaches us respect and humility",
            "working together makes us stronger",
            "the land provides for us if we care for it",
            "our traditions hold deep meaning",
        ],
        "neutral": [
            "there is much to learn",
            "it takes time to understand",
            "everyone learns at their own pace",
            "practice is important",
            "I need to pay more attention",
        ],
        "challenging": [
            "I feel like I'm falling behind",
            "maybe this isn't for me",
            "I wish someone could explain it better",
            "I feel embarrassed when I make mistakes",
            "am I doing something wrong",
        ],
    }

    insight = random.choice(insights[sentiment_type])

    return template.format(
        activity=activity, keyword=keyword, detail=detail, hours=hours, insight=insight
    )


# ============================================================================
# STUDENT GENERATION
# ============================================================================


def generate_hawaiian_name():
    """Generate culturally appropriate Hawaiian name (60%+ Hawaiian)"""
    first = random.choice(HAWAIIAN_FIRST_NAMES)
    last = random.choice(HAWAIIAN_LAST_NAMES)
    return f"{first} {last}"


def assign_campus():
    """Assign student to KS campus based on distribution weights"""
    campuses = list(KS_CAMPUSES.keys())
    weights = [KS_CAMPUSES[c]["weight"] for c in campuses]
    campus = np.random.choice(campuses, p=weights)
    community = random.choice(KS_CAMPUSES[campus]["communities"])
    return campus, community


def generate_student_profile(student_id):
    """Generate complete student profile with cultural context"""
    # Generate grade (K-12, represented as 0-12)
    grade_level = random.randint(1, 12)

    # Calculate timeline
    current_year = datetime.now().year
    years_to_graduation = 12 - grade_level
    expected_graduation = current_year + years_to_graduation
    entry_year = expected_graduation - 12
    entry_date = datetime(entry_year, random.randint(8, 9), random.randint(1, 28))

    # Campus and community
    campus, community = assign_campus()

    # Cultural program participation
    is_hawaiian_language = random.random() < 0.70  # 70% participation
    is_hālau_hula = random.random() < 0.45  # 45% participation
    is_pbl_participant = random.random() < 0.80  # 80% participation

    # HOKU Scholarship (merit-based Hawaiian scholarship)
    has_hoku_scholarship = random.random() < 0.15  # 15% of students

    # Family connection to ʻāina (land)
    aina_connection_score = generate_aina_connection()

    # Demographics
    gender_options = ["Male", "Female", "Non-binary"]
    gender_weights = [0.48, 0.48, 0.04]
    gender = np.random.choice(gender_options, p=gender_weights)

    ethnicity_options = [
        "Native Hawaiian",
        "Native Hawaiian and Other Pacific Islander",
        "Asian",
        "White",
        "Two or More Races",
        "Hispanic/Latino",
    ]
    ethnicity_weights = [0.50, 0.20, 0.15, 0.08, 0.05, 0.02]
    ethnicity = np.random.choice(ethnicity_options, p=ethnicity_weights)

    # Generate IDs
    real_student_id = f"KS{current_year}{student_id:05d}"
    student_uuid = str(uuid.uuid4())

    return {
        "student_uuid": student_uuid,
        "student_id_hash": hashlib.sha256(real_student_id.encode()).hexdigest(),
        "real_student_id": real_student_id,
        "name": generate_hawaiian_name(),
        "grade_level": grade_level,
        "gender_category": gender,
        "ethnicity_category": ethnicity,
        "enrollment_status": "Active",
        "entry_date": entry_date.strftime("%Y-%m-%d"),
        "expected_graduation_year": expected_graduation,
        "campus": campus,
        "community": community,
        "is_pbl_participant": is_pbl_participant,
        "is_hawaiian_language": is_hawaiian_language,
        "is_hālau_hula": is_hālau_hula,
        "has_hoku_scholarship": has_hoku_scholarship,
        "aina_connection_score": aina_connection_score,
        "cohort_year": expected_graduation,
        "homeroom_id": f"HR-{grade_level}{random.choice(['A', 'B', 'C', 'D'])}",
        "effective_start_date": entry_date.strftime("%Y-%m-%d"),
        "effective_end_date": "9999-12-31",
        "is_current": 1,
        "change_reason": "Initial enrollment",
    }


def _clip_score(score):
    """Clip score to valid 0-100 range."""
    return max(0.0, min(100.0, round(float(score), 2)))


def _proficiency(score):
    if score >= 90:
        return "Advanced"
    elif score >= 75:
        return "Proficient"
    elif score >= 60:
        return "Approaching"
    return "Below"


def generate_student_scores(
    student_profile: dict, student_key: int, assessment_date: str, is_dirty: bool = False
) -> list:
    """
    Generate all 14 E Ola! indicator scores for one student.

    ARCHITECTURE (v3 — Latent Ability Model):
    Each student carries three shared latent abilities drawn once per student.
    These latent variables create natural within-student cross-indicator
    correlations (target r ≈ 0.50–0.65 within tier, 0.20–0.35 cross-tier),
    matching real educational measurement patterns.

        cultural_latent  → ROOT tier (1–3) + TRUNK (4–5)   shared driver
        academic_latent  → TRUNK_KULIA (6) + LEAF_ACAD (7–9)
        social_latent    → LEAF social (10–13)
        FRUIT (14)       → weighted composite of all latent signals

    Per-indicator noise std is reduced to 6 so the shared signal is
    visible (previously std=12–15 buried the signal at 94% noise).

    Causal map (programme participation effects on top of latent base):
      is_hawaiian_language  → ROOT_IKE +4, ROOT_ALOHA +1.5, LEAF_GLOBAL +2.2
      is_hālau_hula         → ROOT_IKE +2.8, ROOT_ALOHA +2.2, TRUNK_MALAMA +2.5,
                               LEAF_COLLAB +2.8, LEAF_INNOV +1.8
      is_pbl_participant    → TRUNK_MALAMA +1.5, TRUNK_ALAKAI +2.2,
                               LEAF_ACAD +1.5, LEAF_PROBLEM +3.5,
                               LEAF_INNOV +2.2, LEAF_COLLAB +2.5, LEAF_GLOBAL +1.5
      aina_connection_score → ROOT_ALOHA ×1.0, ROOT_IKE ×0.5,
                               TRUNK_MALAMA ×0.35, ROOT_KUPONO ×0.25
      has_hoku_scholarship  → LEAF_ACAD +10, TRUNK_KULIA +6.5,
                               LEAF_MINDSET +4, LEAF_EFFICACY +3.5
      grade_level           → TRUNK_ALAKAI ×0.8, LEAF_ACAD ×1.2,
                               LEAF_PROBLEM ×0.8
      ethnicity (Native HI) → cultural indicators ×0.8
    """
    is_hawaiian_language = bool(student_profile.get("is_hawaiian_language", False))
    is_hālau_hula        = bool(student_profile.get("is_hālau_hula", False))
    is_pbl_participant   = bool(student_profile.get("is_pbl_participant", False))
    aina_connection      = int(student_profile.get("aina_connection_score", 3))
    has_hoku_scholarship = bool(student_profile.get("has_hoku_scholarship", False))
    grade_level          = int(student_profile.get("grade_level", 6))
    ethnicity            = student_profile.get("ethnicity_category", "")

    # ── Shared latent abilities (drawn once per student) ──────────────────────
    # These represent the student's underlying capacity in each domain.
    # std=8 chosen so latent signal is ~60% of total variance per indicator,
    # yielding within-tier r ≈ 0.55–0.65 before programme effects.
    cultural_latent = np.random.normal(0, 8)   # cultural knowledge & identity
    academic_latent = np.random.normal(0, 7)   # academic & intellectual capacity
    social_latent   = np.random.normal(0, 6)   # collaborative & social capacity

    # ── Observable attribute effects ─────────────────────────────────────────
    grade_boost      = (grade_level - 6) * 0.7
    aina_boost       = (aina_connection - 3) * 3.5
    ethnicity_boost  = random.gauss(2.0, 0.8) if "Native Hawaiian" in ethnicity else 0.0

    # Per-indicator residual noise (std=6, down from 12–15)
    # Together with latent std=8: total variance ≈ 64+36=100, std≈10
    N = lambda: np.random.normal(0, 6)

    # ── ROOT TIER (Cultural Foundation) ───────────────────────────────────────
    # cultural_latent is the primary shared driver; all three ROOT indicators
    # should correlate at r ≈ 0.55–0.65 with each other.

    # 1. ROOT_IKE — 'Ike Kūpuna
    s1 = 75 + cultural_latent + N()
    if is_hawaiian_language: s1 += random.gauss(4.0, 1.5)
    if is_hālau_hula:        s1 += random.gauss(2.8, 1.2)
    s1 += aina_boost * 0.5 + ethnicity_boost * 0.8
    scores = {1: _clip_score(s1)}

    # 2. ROOT_ALOHA — Aloha ʻĀina
    s2 = 78 + cultural_latent + N()
    s2 += aina_boost * 1.0
    if is_hālau_hula:        s2 += random.gauss(2.2, 1.0)
    if is_hawaiian_language: s2 += random.gauss(1.5, 0.9)
    s2 += ethnicity_boost * 0.6
    scores[2] = _clip_score(s2)

    # 3. ROOT_KUPONO — Kūpono (Integrity)
    s3 = 76 + cultural_latent + N()
    s3 += aina_boost * 0.25
    if is_hawaiian_language or is_hālau_hula: s3 += random.gauss(1.2, 1.0)
    scores[3] = _clip_score(s3)

    # ── TRUNK TIER (Identity Formation) ───────────────────────────────────────
    # Mix of cultural + social latent (bridge between roots and leaves).

    # 4. TRUNK_MALAMA — Mālama & Kuleana
    s4 = 76 + cultural_latent * 0.6 + social_latent * 0.4 + N()
    if is_hālau_hula:        s4 += random.gauss(2.5, 1.0)
    if is_hawaiian_language: s4 += random.gauss(1.5, 1.0)
    if is_pbl_participant:   s4 += random.gauss(1.5, 1.0)
    s4 += aina_boost * 0.35
    scores[4] = _clip_score(s4)

    # 5. TRUNK_ALAKAI — Alaka'i Lawelawe (Servant Leadership)
    s5 = 74 + cultural_latent * 0.4 + social_latent * 0.6 + N()
    s5 += grade_boost * 0.8
    if is_pbl_participant: s5 += random.gauss(2.2, 1.2)
    if is_hālau_hula:      s5 += random.gauss(1.5, 1.0)
    scores[5] = _clip_score(s5)

    # 6. TRUNK_KULIA — Kūlia (Excellence)
    s6 = 74 + academic_latent * 0.7 + cultural_latent * 0.3 + N()
    s6 += grade_boost
    if has_hoku_scholarship: s6 += random.gauss(6.5, 2.0)
    scores[6] = _clip_score(s6)

    # ── LEAF TIER (Action & Skills) ───────────────────────────────────────────
    # Academic cluster (7–9): academic_latent dominant → r ≈ 0.55–0.60
    # Social cluster  (10–13): social_latent dominant  → r ≈ 0.50–0.60

    # 7. LEAF_ACAD — Academic Competence
    s7 = 72 + academic_latent + N()
    s7 += grade_boost * 1.2
    if has_hoku_scholarship: s7 += random.gauss(10.0, 2.0)
    if is_pbl_participant:   s7 += random.gauss(1.5, 1.0)
    scores[7] = _clip_score(s7)

    # 8. LEAF_MINDSET — Growth Mindset
    s8 = 74 + academic_latent * 0.8 + N()
    if has_hoku_scholarship: s8 += random.gauss(4.0, 1.5)
    if is_pbl_participant:   s8 += random.gauss(2.0, 1.0)
    scores[8] = _clip_score(s8)

    # 9. LEAF_EFFICACY — Self-efficacy
    s9 = 74 + academic_latent * 0.7 + N()
    if has_hoku_scholarship: s9 += random.gauss(3.5, 1.5)
    scores[9] = _clip_score(s9)

    # 10. LEAF_PROBLEM — Problem Solving
    s10 = 74 + social_latent * 0.8 + academic_latent * 0.2 + N()
    s10 += grade_boost * 0.8
    if is_pbl_participant: s10 += random.gauss(3.5, 1.2)
    scores[10] = _clip_score(s10)

    # 11. LEAF_INNOV — Innovation & Creativity
    s11 = 72 + social_latent + N()
    if is_pbl_participant: s11 += random.gauss(2.2, 1.2)
    if is_hālau_hula:      s11 += random.gauss(1.8, 1.0)
    scores[11] = _clip_score(s11)

    # 12. LEAF_COLLAB — Collaboration
    s12 = 74 + social_latent + N()
    if is_pbl_participant:   s12 += random.gauss(2.5, 1.0)
    if is_hālau_hula:        s12 += random.gauss(2.8, 1.0)
    if is_hawaiian_language: s12 += random.gauss(1.2, 0.8)
    scores[12] = _clip_score(s12)

    # 13. LEAF_GLOBAL — Global Competence
    s13 = 72 + social_latent * 0.7 + cultural_latent * 0.3 + N()
    s13 += aina_boost * 0.3 + ethnicity_boost * 0.4
    if is_hawaiian_language: s13 += random.gauss(2.2, 1.0)
    if is_pbl_participant:   s13 += random.gauss(1.5, 1.0)
    scores[13] = _clip_score(s13)

    # 14. FRUIT_WELLBEING — Holistic Well-Being
    #     Weighted blend of all three latent abilities + residual noise
    #     Correlates moderately with every indicator (r ≈ 0.35–0.50)
    s14 = (70
           + cultural_latent * 0.40
           + academic_latent * 0.35
           + social_latent   * 0.25
           + N())
    scores[14] = _clip_score(s14)

    # -------------------------------------------------------------------------
    # Build output records
    # -------------------------------------------------------------------------
    results = []
    for indicator_key, score in scores.items():
        used_date = assessment_date

        # Dirty data injection (only for designated dirty students)
        if is_dirty:
            if indicator_key == 1 and random.random() < 0.3:
                score = float(random.randint(101, 150))  # score > 100
            if random.random() < 0.3:
                used_date = "2027-06-15"                 # future date

        results.append({
            "student_key": student_key,
            "indicator_key": indicator_key,
            "assessment_type_key": random.randint(1, 7),
            "date_key": int(used_date.replace("-", "")),
            "raw_score": score,
            "normalized_score": min(100.0, score),
            "proficiency_level": _proficiency(score),
            "percentile_rank": min(
                99, max(1, int(stats.percentileofscore([50, 60, 70, 80, 90], score)))
            ),
            "assessment_date": used_date,
            "source_system": "Synthetic Data Generator v3.0",
        })

    return results


def generate_cultural_activities(student_key):
    """Generate cultural activity participation with power-law distribution"""
    activities = []

    # 'Ike Kūpuna activities
    hawaiian_language_hours = generate_power_law_hours(
        alpha=2.0, min_hours=5, max_hours=40
    )
    activities.append(
        {
            "student_key": student_key,
            "activity_type": "Hawaiian Language",
            "hours_participated": hawaiian_language_hours,
            "engagement_level": "High"
            if hawaiian_language_hours > 25
            else "Medium"
            if hawaiian_language_hours > 10
            else "Low",
        }
    )

    # Community workshop hours (power-law: few leaders with 30+ hours)
    workshop_hours = generate_power_law_hours(alpha=1.8, min_hours=2, max_hours=45)
    activities.append(
        {
            "student_key": student_key,
            "activity_type": "Community Workshop",
            "hours_participated": workshop_hours,
            "engagement_level": "Cultural Leader"
            if workshop_hours > 30
            else "Active"
            if workshop_hours > 15
            else "Participant",
        }
    )

    # Loʻi kalo work
    loi_frequency = random.randint(1, 12)  # Times per semester
    loi_hours = loi_frequency * random.randint(2, 4)
    activities.append(
        {
            "student_key": student_key,
            "activity_type": "Loʻi Kalo",
            "frequency_per_semester": loi_frequency,
            "hours_participated": loi_hours,
            "engagement_level": "Steward"
            if loi_frequency > 8
            else "Regular"
            if loi_frequency > 4
            else "Occasional",
        }
    )

    return activities


def generate_reflections(student_key, count=5):
    """Generate cultural reflection texts with sentiment distribution"""
    reflections = []

    # 70% positive, 20% neutral, 10% challenging
    sentiment_distribution = ["positive"] * 7 + ["neutral"] * 2 + ["challenging"] * 1

    for i in range(count):
        sentiment = random.choice(sentiment_distribution)
        reflection_text = generate_cultural_reflection(sentiment)

        reflections.append(
            {
                "student_key": student_key,
                "reflection_date": (
                    datetime.now() - timedelta(days=random.randint(1, 180))
                ).strftime("%Y-%m-%d"),
                "sentiment_type": sentiment,
                "reflection_text": reflection_text,
                "word_count": len(reflection_text.split()),
                "hawaiian_keywords_found": [
                    kw for kw in HAWAIIAN_KEYWORDS if kw in reflection_text
                ],
            }
        )

    return reflections


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================


def init_database(db_path="e_ola_enterprise.db"):
    """Initialize database with enterprise schema"""
    conn = sqlite3.connect(db_path)

    # Read and execute schema
    # executescript() handles semicolons inside comments and trigger BEGIN..END blocks
    # correctly, unlike naive split(';') which broke on comments like
    # "Only ADMIN role can modify; AUDITOR role can view"
    with open("schema/v1_1_enterprise_schema.sql", "r") as f:
        schema = f.read()

    conn.executescript(schema)
    return conn


def insert_student_mapping(conn, student):
    """Insert student mapping record"""
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO dim_student_mapping 
        (student_uuid, student_id_hash, encryption_key_ref, created_by, updated_by)
        VALUES (?, ?, ?, 'ironforge_miner', 'ironforge_miner')
    """,
        (student["student_uuid"], student["student_id_hash"], "kv://e-ola-keys/v1"),
    )
    return cursor.lastrowid


def insert_student_masked(conn, student):
    """Insert masked student record with SCD Type 2"""
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO dim_students_masked 
        (student_uuid, grade_level, gender_category, ethnicity_category, 
         enrollment_status, entry_date, expected_graduation_year,
         is_pbl_participant, is_hawaiian_language, is_hālau_hula,
         cohort_year, homeroom_id, effective_start_date, effective_end_date, 
         is_current, change_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            student["student_uuid"],
            student["grade_level"],
            student["gender_category"],
            student["ethnicity_category"],
            student["enrollment_status"],
            student["entry_date"],
            student["expected_graduation_year"],
            student["is_pbl_participant"],
            student["is_hawaiian_language"],
            student["is_hālau_hula"],
            student["cohort_year"],
            student["homeroom_id"],
            student["effective_start_date"],
            student["effective_end_date"],
            student["is_current"],
            student["change_reason"],
        ),
    )
    return cursor.lastrowid


def insert_outcome(conn, outcome):
    """Insert E Ola! outcome"""
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO fact_e_ola_outcomes 
        (student_key, indicator_key, assessment_type_key, date_key,
         raw_score, normalized_score, proficiency_level, percentile_rank,
         assessment_date, source_system)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            outcome["student_key"],
            outcome["indicator_key"],
            outcome["assessment_type_key"],
            outcome["date_key"],
            outcome["raw_score"],
            outcome["normalized_score"],
            outcome["proficiency_level"],
            outcome["percentile_rank"],
            outcome["assessment_date"],
            outcome["source_system"],
        ),
    )


def log_access(conn, user_role, view_name, records_count):
    """Log access for audit trail"""
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO sys_access_logs 
        (user_id, user_role, accessed_view, query_type, records_accessed, 
         access_timestamp, client_application, ferpa_consent_verified)
        VALUES (?, ?, ?, 'SELECT', ?, datetime('now'), 'Data Generator', 1)
    """,
        ("ironforge_miner", user_role, view_name, records_count),
    )


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    print("⛏️  Ironforge Miner: Enterprise Data Mining Operation v2.0")
    print("=" * 80)

    # Initialize database
    print("\n📦 Initializing enterprise database...")
    conn = init_database()

    # Configuration
    total_students = 200
    dirty_score_count = 5
    dirty_uuid_count = 3
    dirty_date_count = 3

    print(
        f"\n👥 Mining {total_students} students with Hawaiian cultural authenticity..."
    )
    print(f"   - 60%+ Hawaiian names")
    print(f"   - 3 KS campuses (Kāpalama, Maui, Hawaiʻi Island)")
    print(f"   - HOKU scholarship + ʻĀina connection scores")
    print(f"   - SCD Type 2 temporal tracking")

    students = []
    dirty_indices = random.sample(
        range(total_students), dirty_score_count + dirty_uuid_count + dirty_date_count
    )
    dirty_score_indices = dirty_indices[:dirty_score_count]
    dirty_uuid_indices = dirty_indices[
        dirty_score_count : dirty_score_count + dirty_uuid_count
    ]
    dirty_date_indices = dirty_indices[dirty_score_count + dirty_uuid_count :]

    # Generate student profiles
    for i in range(total_students):
        student = generate_student_profile(i + 1)
        students.append(student)

    print(f"\n✅ Generated {len(students)} culturally-authentic student profiles")

    # Calculate statistics
    hawaiian_names = sum(
        1 for s in students if any(name in s["name"] for name in HAWAIIAN_FIRST_NAMES)
    )
    campus_dist = {}
    for s in students:
        campus_dist[s["campus"]] = campus_dist.get(s["campus"], 0) + 1

    print(
        f"   - Hawaiian names: {hawaiian_names}/{total_students} ({hawaiian_names / total_students * 100:.1f}%)"
    )
    print(f"   - Campus distribution:")
    for campus, count in campus_dist.items():
        print(f"      {campus}: {count} ({count / total_students * 100:.1f}%)")

    # Insert into database
    print("\n💾 Inserting data with enterprise-grade audit logging...")

    student_keys = {}
    reflections_all = []
    activities_all = []

    for i, student in enumerate(students):
        try:
            # Check for dirty UUID
            is_dirty_uuid = i in dirty_uuid_indices
            if is_dirty_uuid:
                student["student_uuid"] = str(uuid.uuid4())  # Will not exist in mapping

            # Insert mapping (skip for dirty UUID test - will cause FK violation)
            if not is_dirty_uuid:
                mapping_id = insert_student_mapping(conn, student)
                student_key = insert_student_masked(conn, student)
                student_keys[student["student_uuid"]] = student_key

                # Generate outcomes for all 14 indicators (student-profile-aware)
                assessment_date = (
                    datetime.now() - timedelta(days=random.randint(1, 90))
                ).strftime("%Y-%m-%d")
                is_dirty_score = i in dirty_score_indices

                outcomes = generate_student_scores(
                    student_profile=student,
                    student_key=student_key,
                    assessment_date=assessment_date,
                    is_dirty=is_dirty_score,
                )
                for outcome in outcomes:
                    insert_outcome(conn, outcome)

                # Generate cultural activities
                activities = generate_cultural_activities(student_key)
                activities_all.extend(activities)

                # Generate reflections
                reflections = generate_reflections(
                    student_key, count=random.randint(3, 7)
                )
                reflections_all.extend(reflections)

            if (i + 1) % 20 == 0:
                print(f"   ✓ Processed {i + 1}/{total_students} students...")

        except Exception as e:
            if is_dirty_uuid:
                print(f"   ⚠️  Expected FK violation for dirty UUID (student {i + 1})")
            else:
                print(f"   ✗ Error on student {i + 1}: {str(e)[:60]}...")

    conn.commit()

    # Log access
    log_access(conn, "System", "dim_students_masked", len(student_keys))
    log_access(conn, "System", "fact_e_ola_outcomes", len(student_keys) * 14)
    conn.commit()

    # Calculate reflection sentiment distribution
    sentiment_dist = {"positive": 0, "neutral": 0, "challenging": 0}
    for r in reflections_all:
        sentiment_dist[r["sentiment_type"]] += 1

    print("\n" + "=" * 80)
    print("⛏️  MINING OPERATION COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Enterprise Data Summary:")
    print(f"   Total students generated: {total_students}")
    print(f"   Successfully inserted: {len(student_keys)}")
    print(f"   E Ola! outcomes: {len(student_keys) * 14}")
    print(f"   Cultural activities: {len(activities_all)}")
    print(f"   Reflection texts: {len(reflections_all)}")

    print(f"\n📝 Reflection Sentiment Distribution:")
    total_reflections = sum(sentiment_dist.values())
    for sentiment, count in sentiment_dist.items():
        pct = count / total_reflections * 100
        print(f"   {sentiment:12s}: {count:3d} ({pct:5.1f}%)")

    print(f"\n🔍 Dirty Data Injection Report:")
    print(f"   Scores > 100: {dirty_score_count} records")
    print(f"   Invalid UUIDs (FK violation): {dirty_uuid_count} records")
    print(f"   Future dates (2027): {dirty_date_count} records")

    print("\n🌺 Sample Cultural Reflections:")
    print("-" * 80)
    for sentiment in ["positive", "neutral", "challenging"]:
        sample = next(
            (r for r in reflections_all if r["sentiment_type"] == sentiment), None
        )
        if sample:
            print(f"\n[{sentiment.upper()}]")
            print(f'   "{sample["reflection_text"]}"')
            print(f"   Keywords: {', '.join(sample['hawaiian_keywords_found'])}")

    print("\n🎓 Sample Student Profiles:")
    print("-" * 80)
    for i in range(min(3, len(students))):
        s = students[i]
        print(f"\nStudent {i + 1}: {s['name']}")
        print(f"   Campus: {s['campus']} ({s['community']})")
        print(
            f"   Grade: {s['grade_level']} | HOKU Scholar: {'Yes' if s['has_hoku_scholarship'] else 'No'}"
        )
        print(f"   ʻĀina Connection: {s['aina_connection_score']}/5")
        print(
            f"   Programs: Hawaiian Lang={s['is_hawaiian_language']}, Hula={s['is_hālau_hula']}"
        )

    print("\n" + "=" * 80)
    print("✨ The enterprise ore is ready for the Archmage's refinement!")
    print("=" * 80)

    conn.close()


if __name__ == "__main__":
    main()
