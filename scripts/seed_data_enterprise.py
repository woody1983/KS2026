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


def generate_e_ola_outcomes(
    student_key, indicator_key, assessment_date, is_dirty=False
):
    """Generate E Ola! outcomes with realistic distributions"""

    # Base score (normal distribution)
    if indicator_key == 1:  # 'Ike Kūpuna - Hawaiian language
        base_score = generate_normal_score(mean=75, std=15)
    elif indicator_key == 2:  # Aloha ʻĀina - Land connection
        base_score = generate_normal_score(mean=78, std=12)
    elif indicator_key in [3, 4, 5]:  # Roots
        base_score = generate_normal_score(mean=76, std=14)
    elif indicator_key in [6, 7, 8]:  # Trunk
        base_score = generate_normal_score(mean=72, std=13)
    elif indicator_key in [9, 10, 11, 12, 13, 14, 15]:  # Leaves
        base_score = generate_normal_score(mean=74, std=16)
    else:  # Fruits
        base_score = generate_normal_score(mean=70, std=14)

    # Dirty data injection: score > 100
    if is_dirty and random.random() < 0.3:
        base_score = random.randint(101, 150)

    # Dirty data injection: future date
    if is_dirty and random.random() < 0.3:
        assessment_date = "2027-06-15"

    # Proficiency level
    if base_score >= 90:
        proficiency = "Advanced"
    elif base_score >= 75:
        proficiency = "Proficient"
    elif base_score >= 60:
        proficiency = "Approaching"
    else:
        proficiency = "Below"

    return {
        "student_key": student_key,
        "indicator_key": indicator_key,
        "assessment_type_key": random.randint(1, 7),
        "date_key": int(assessment_date.replace("-", "")),
        "raw_score": base_score,
        "normalized_score": min(100, base_score),
        "proficiency_level": proficiency,
        "percentile_rank": min(
            99, max(1, int(stats.percentileofscore([50, 60, 70, 80, 90], base_score)))
        ),
        "assessment_date": assessment_date,
        "source_system": "Synthetic Data Generator v2.0",
    }


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
    with open("schema/v1_1_enterprise_schema.sql", "r") as f:
        schema = f.read()

    statements = [s.strip() for s in schema.split(";") if s.strip()]
    for statement in statements:
        try:
            conn.execute(statement)
        except sqlite3.Error as e:
            pass

    conn.commit()
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

                # Generate outcomes for 14 indicators
                assessment_date = (
                    datetime.now() - timedelta(days=random.randint(1, 90))
                ).strftime("%Y-%m-%d")
                is_dirty_score = i in dirty_score_indices

                for indicator_key in range(1, 15):
                    outcome = generate_e_ola_outcomes(
                        student_key,
                        indicator_key,
                        assessment_date,
                        is_dirty=(is_dirty_score and indicator_key == 1),
                    )
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
