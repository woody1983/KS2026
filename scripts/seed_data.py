#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E Ola! Learner Analytics System - Seed Data Generator
Author: The Ironforge Miner (铁炉堡矿工)
Description: High-fidelity synthetic data generation for Hawaiian students
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

# Initialize Faker with Hawaiian locale support
fake = Faker(["en_US"])
Faker.seed(42)
np.random.seed(42)

# ============================================================================
# HAWAIIAN CULTURAL DATASETS
# ============================================================================

HAWAIIAN_FIRST_NAMES = [
    # Male names
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
    "Kekoa",
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
    # Female names
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
]

HAWAIIAN_COMMUNITIES = [
    "Waimānalo",
    "Waiʻanae",
    "Maui",
    "Molokaʻi",
    "Lānaʻi",
    "Kauaʻi",
    "Hilo",
    "Kona",
    "Kahului",
    "Līhuʻe",
    "Kāneʻohe",
    "Kailua",
    "ʻEwa Beach",
    "Mākaha",
    "Nānākuli",
    "Haleʻiwa",
    "Waialua",
    "Wahiawā",
    "Pearl City",
    "Mililani",
    "Kapaʻa",
    "Waimea",
    "Koloa",
    "Pāʻia",
    "Lahaina",
    "Kīhei",
]

CULTURAL_ACTIVITIES = [
    "Hula ʻauana (modern hula)",
    "Hula kahiko (ancient hula)",
    "ʻŌlelo Hawaiʻi class",
    "Loʻi kalo (taro cultivation)",
    "Lāʻau lapaʻau (herbal medicine)",
    "Hoʻokele (navigation)",
    "Mele composition",
    "Moʻolelo (storytelling)",
    "Lauhala weaving",
    "Kapa making",
    "Pāʻū riding",
    "Canoe paddling",
    "Fishpond restoration",
    "Irrigation systems (ʻauwai)",
    "Star navigation",
    "Chant (oli) learning",
    "Feather work",
    "Stone tool making",
]

CULTURAL_REFLECTION_TEMPLATES = [
    "Today I learned about {topic}. It made me feel {emotion} because {reason}.",
    "When we practiced {activity}, I realized that {insight}.",
    "My kumu taught us about {topic}. I think it's important because {reason}.",
    "During {activity}, I felt connected to my ancestors because {connection}.",
    "Learning {topic} helped me understand {insight} about Hawaiian culture.",
    "The {activity} was challenging but I learned that {lesson}.",
    "My favorite part today was {activity} because {reason}.",
    "I never knew that {fact}. Now I understand why {insight}.",
]

REFLECTION_TOPICS = [
    "kalo (taro)",
    "ʻāina (land)",
    "moʻokūʻauhau (genealogy)",
    "kuleana (responsibility)",
    "aloha ʻāina",
    "mālama honua",
    "kupuna (ancestors)",
    "wahi pana (sacred places)",
    "kai (ocean)",
    "mauna (mountains)",
    "makani (winds)",
    "ua (rains)",
]

REFLECTION_EMOTIONS = [
    "proud",
    "grateful",
    "connected",
    "inspired",
    "peaceful",
    "excited",
    "humbled",
    "respectful",
    "joyful",
    "hopeful",
]

# ============================================================================
# STATISTICAL DISTRIBUTIONS
# ============================================================================


def generate_normal_score(mean=75, std=12, min_val=0, max_val=100):
    """Generate normally distributed score with bounds"""
    score = np.random.normal(mean, std)
    return max(min_val, min(max_val, round(score, 2)))


def generate_power_law_participation(min_val=0, max_val=100, alpha=2.5):
    """Generate power-law distributed participation (few highly engaged, many low)"""
    # Use Pareto distribution for power-law behavior
    val = (np.random.pareto(alpha) * 10) % max_val
    return round(min(val, max_val), 2)


def generate_proficiency_level(score):
    """Convert score to proficiency level"""
    if score >= 90:
        return "Advanced"
    elif score >= 75:
        return "Proficient"
    elif score >= 60:
        return "Approaching"
    else:
        return "Below"


# ============================================================================
# DATA GENERATION FUNCTIONS
# ============================================================================


def generate_hawaiian_name():
    """Generate culturally appropriate Hawaiian name"""
    first = random.choice(HAWAIIAN_FIRST_NAMES)
    last = random.choice(HAWAIIAN_LAST_NAMES)
    return f"{first} {last}"


def generate_student_uuid():
    """Generate UUID for student mapping"""
    return str(uuid.uuid4())


def generate_student_id_hash(real_id):
    """Generate SHA-256 hash of real student ID"""
    return hashlib.sha256(real_id.encode()).hexdigest()


def generate_cultural_reflection():
    """Generate authentic 10-year-old student cultural reflection"""
    template = random.choice(CULTURAL_REFLECTION_TEMPLATES)
    topic = random.choice(REFLECTION_TOPICS)
    emotion = random.choice(REFLECTION_EMOTIONS)
    activity = random.choice(CULTURAL_ACTIVITIES)

    reasons = [
        f"it connects me to my {random.choice(['kupuna', 'family', 'culture'])}",
        f"I learned about {random.choice(['respect', 'patience', 'teamwork'])}",
        f"it helps me understand who I am",
        f"our land is important",
    ]

    insights = [
        "our ancestors were very smart",
        "we must take care of the land",
        "everything is connected",
        "traditions help us remember",
    ]

    connections = [
        "my tutu told me similar stories",
        "I feel the mana in the ʻāina",
        "the oli carries ancient wisdom",
    ]

    facts = [
        "kalo is our older brother",
        "Hawaiians were expert navigators",
        "every mountain has a name and story",
        "the ocean provides for us",
    ]

    return template.format(
        topic=topic,
        emotion=emotion,
        activity=activity,
        reason=random.choice(reasons),
        insight=random.choice(insights),
        connection=random.choice(connections),
        fact=random.choice(facts),
        lesson=random.choice(insights),
    )


def generate_dirty_data_student(student_id):
    """Generate student with intentional logical errors for testing"""
    error_type = random.choice(
        [
            "invalid_grade",
            "future_entry",
            "negative_score",
            "null_required",
            "invalid_uuid",
            "mismatched_dates",
        ]
    )

    base_student = generate_clean_student(student_id)

    if error_type == "invalid_grade":
        base_student["grade_level"] = random.choice([0, 13, 99, -1])
    elif error_type == "future_entry":
        base_student["entry_date"] = (datetime.now() + timedelta(days=365)).strftime(
            "%Y-%m-%d"
        )
    elif error_type == "negative_score":
        base_student["test_scores"] = [-5, -10, 150]
    elif error_type == "null_required":
        base_student["student_uuid"] = None
    elif error_type == "invalid_uuid":
        base_student["student_uuid"] = "not-a-valid-uuid-12345"
    elif error_type == "mismatched_dates":
        base_student["entry_date"] = "2020-01-01"
        base_student["expected_graduation_year"] = 2019

    base_student["_error_type"] = error_type
    return base_student


def generate_clean_student(student_id):
    """Generate clean, valid student record"""
    # Generate grade level (K-12, represented as 0-12)
    grade_level = random.randint(1, 12)

    # Calculate cohort year based on grade
    current_year = datetime.now().year
    years_to_graduation = 12 - grade_level
    expected_graduation = current_year + years_to_graduation

    # Entry date (between 1-12 years ago depending on grade)
    entry_year = expected_graduation - 12
    entry_date = datetime(entry_year, random.randint(8, 9), random.randint(1, 28))

    # Generate participation in cultural programs
    is_hawaiian_language = random.random() < 0.65  # 65% participation
    is_hālau_hula = random.random() < 0.40  # 40% participation
    is_pbl_participant = random.random() < 0.75  # 75% participation

    # Generate demographic categories
    gender_options = ["Male", "Female", "Non-binary", "Prefer not to say"]
    gender_weights = [0.48, 0.48, 0.02, 0.02]
    gender = np.random.choice(gender_options, p=gender_weights)

    ethnicity_options = [
        "Native Hawaiian",
        "Native Hawaiian and Other Pacific Islander",
        "Asian",
        "White",
        "Two or More Races",
        "Hispanic/Latino",
    ]
    ethnicity_weights = [0.45, 0.20, 0.15, 0.10, 0.07, 0.03]
    ethnicity = np.random.choice(ethnicity_options, p=ethnicity_weights)

    # Generate real student ID (would be encrypted in production)
    real_student_id = f"KS{current_year}{student_id:05d}"

    return {
        "student_uuid": generate_student_uuid(),
        "student_id_hash": generate_student_id_hash(real_student_id),
        "real_student_id": real_student_id,  # For reference only
        "name": generate_hawaiian_name(),
        "grade_level": grade_level,
        "gender_category": gender,
        "ethnicity_category": ethnicity,
        "enrollment_status": "Active",
        "entry_date": entry_date.strftime("%Y-%m-%d"),
        "expected_graduation_year": expected_graduation,
        "is_pbl_participant": is_pbl_participant,
        "is_hawaiian_language": is_hawaiian_language,
        "is_hālau_hula": is_hālau_hula,
        "cohort_year": expected_graduation,
        "homeroom_id": f"HR-{grade_level}{random.choice(['A', 'B', 'C', 'D'])}",
        "community": random.choice(HAWAIIAN_COMMUNITIES),
        "cultural_activities": random.sample(
            CULTURAL_ACTIVITIES, k=random.randint(1, 5)
        ),
    }


def generate_e_ola_scores(student_key, indicator_keys, date_key):
    """Generate E Ola! indicator scores for a student"""
    scores = []

    for indicator_key in indicator_keys:
        # Different indicators have different score distributions
        if indicator_key in [1, 2, 3]:  # Roots (Cultural) - generally higher
            score = generate_normal_score(mean=78, std=10)
        elif indicator_key in [4, 5, 6]:  # Trunk (Identity)
            score = generate_normal_score(mean=72, std=12)
        elif indicator_key in [7, 8, 9, 10, 11, 12, 13]:  # Leaves (Skills)
            score = generate_normal_score(mean=75, std=15)
        else:  # Fruits (Well-being)
            score = generate_normal_score(mean=70, std=13)

        scores.append(
            {
                "student_key": student_key,
                "indicator_key": indicator_key,
                "raw_score": score,
                "normalized_score": score,
                "proficiency_level": generate_proficiency_level(score),
                "percentile_rank": min(
                    99,
                    max(1, int(stats.percentileofscore([50, 60, 70, 80, 90], score))),
                ),
                "date_key": date_key,
                "assessment_date": datetime.now().strftime("%Y-%m-%d"),
            }
        )

    return scores


def generate_wellbeing_scores(student_key, date_key):
    """Generate 7-dimensional well-being scores"""
    # Generate scores with correlation (students tend to be consistent across dimensions)
    base_score = np.random.normal(72, 10)

    dimensions = {
        "cultural": max(0, min(100, base_score + np.random.normal(5, 8))),
        "spiritual": max(0, min(100, base_score + np.random.normal(0, 10))),
        "social": max(0, min(100, base_score + np.random.normal(2, 12))),
        "economic": max(0, min(100, base_score + np.random.normal(-3, 15))),
        "physical": max(0, min(100, base_score + np.random.normal(-2, 10))),
        "emotional": max(0, min(100, base_score + np.random.normal(-5, 12))),
        "cognitive": max(0, min(100, base_score + np.random.normal(8, 8))),
    }

    overall = np.mean(list(dimensions.values()))

    if overall >= 80:
        category = "Thriving"
    elif overall >= 65:
        category = "Balanced"
    elif overall >= 50:
        category = "Struggling"
    else:
        category = "Crisis"

    return {
        "student_key": student_key,
        "date_key": date_key,
        "cultural_score": round(dimensions["cultural"], 2),
        "spiritual_score": round(dimensions["spiritual"], 2),
        "social_score": round(dimensions["social"], 2),
        "economic_score": round(dimensions["economic"], 2),
        "physical_score": round(dimensions["physical"], 2),
        "emotional_score": round(dimensions["emotional"], 2),
        "cognitive_score": round(dimensions["cognitive"], 2),
        "overall_wellbeing_score": round(overall, 2),
        "wellbeing_category": category,
        "assessment_date": datetime.now().strftime("%Y-%m-%d"),
    }


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================


def init_database(db_path="e_ola_analytics.db"):
    """Initialize database with schema"""
    conn = sqlite3.connect(db_path)

    # Read and execute schema
    with open("schema/v1_e_ola_schema.sql", "r") as f:
        schema = f.read()

    # Execute schema (split by semicolons to handle multiple statements)
    statements = [s.strip() for s in schema.split(";") if s.strip()]
    for statement in statements:
        try:
            conn.execute(statement)
        except sqlite3.Error as e:
            # Some statements may fail (like CREATE VIEW after table creation)
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


def insert_student_masked(conn, student, student_key):
    """Insert masked student record"""
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO dim_students_masked 
        (student_uuid, grade_level, gender_category, ethnicity_category, 
         enrollment_status, entry_date, expected_graduation_year,
         is_pbl_participant, is_hawaiian_language, is_hālau_hula,
         cohort_year, homeroom_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        ),
    )
    return cursor.lastrowid


def insert_e_ola_outcomes(conn, outcomes):
    """Insert E Ola! outcome records"""
    cursor = conn.cursor()
    for outcome in outcomes:
        cursor.execute(
            """
            INSERT INTO fact_e_ola_outcomes 
            (student_key, indicator_key, assessment_type_key, date_key,
             raw_score, normalized_score, proficiency_level, percentile_rank,
             assessment_date, source_system)
            VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, 'Synthetic Data Generator')
        """,
            (
                outcome["student_key"],
                outcome["indicator_key"],
                outcome["date_key"],
                outcome["raw_score"],
                outcome["normalized_score"],
                outcome["proficiency_level"],
                outcome["percentile_rank"],
                outcome["assessment_date"],
            ),
        )


def insert_wellbeing_measurements(conn, wellbeing):
    """Insert well-being measurement"""
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO fact_wellbeing_measurements 
        (student_key, date_key, assessment_type_key,
         cultural_score, spiritual_score, social_score, economic_score,
         physical_score, emotional_score, cognitive_score,
         overall_wellbeing_score, wellbeing_category, assessment_date, source_system)
        VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Synthetic Data Generator')
    """,
        (
            wellbeing["student_key"],
            wellbeing["date_key"],
            wellbeing["cultural_score"],
            wellbeing["spiritual_score"],
            wellbeing["social_score"],
            wellbeing["economic_score"],
            wellbeing["physical_score"],
            wellbeing["emotional_score"],
            wellbeing["cognitive_score"],
            wellbeing["overall_wellbeing_score"],
            wellbeing["wellbeing_category"],
            wellbeing["assessment_date"],
        ),
    )


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    print("⛏️  Ironforge Miner: Beginning data mining operation...")
    print("=" * 70)

    # Initialize database
    print("\n📦 Initializing database...")
    conn = init_database()

    # Generate students
    total_students = 200
    dirty_count = 10
    clean_count = total_students - dirty_count

    print(f"\n👥 Generating {total_students} students...")
    print(f"   - Clean records: {clean_count}")
    print(f"   - Records with logical errors: {dirty_count}")

    students = []
    dirty_students = []

    # Generate clean students
    for i in range(clean_count):
        student = generate_clean_student(i + 1)
        students.append(student)

    # Generate dirty students
    for i in range(dirty_count):
        student = generate_dirty_data_student(clean_count + i + 1)
        dirty_students.append(student)
        students.append(student)

    # Shuffle to mix dirty records
    random.shuffle(students)

    print(f"\n✅ Generated {len(students)} student profiles")
    print(f"   - Hawaiian names: {len(set(s['name'] for s in students))} unique")
    print(f"   - Grade levels: {set(s['grade_level'] for s in students)}")
    print(f"   - Communities: {len(set(s['community'] for s in students))} unique")

    # Insert into database
    print("\n💾 Inserting data into database...")

    date_key = int(datetime.now().strftime("%Y%m%d"))
    indicator_keys = list(range(1, 15))  # 14 E Ola! indicators

    inserted_count = 0
    error_count = 0

    for i, student in enumerate(students):
        try:
            # Check if this is a dirty record
            is_dirty = "_error_type" in student

            if is_dirty:
                print(
                    f"   ⚠️  Inserting dirty record {i + 1}/{len(students)} (Error: {student['_error_type']})"
                )
            else:
                if (i + 1) % 20 == 0:
                    print(f"   ✓ Inserted {i + 1}/{len(students)} records...")

            # Insert mapping
            mapping_id = insert_student_mapping(conn, student)

            # Insert masked student (this will fail for some dirty records)
            student_key = insert_student_masked(conn, student, mapping_id)

            # Generate and insert E Ola! outcomes
            outcomes = generate_e_ola_scores(student_key, indicator_keys, date_key)
            insert_e_ola_outcomes(conn, outcomes)

            # Generate and insert well-being measurements
            wellbeing = generate_wellbeing_scores(student_key, date_key)
            insert_wellbeing_measurements(conn, wellbeing)

            inserted_count += 1

        except Exception as e:
            error_count += 1
            is_dirty_record = "_error_type" in student
            if is_dirty_record:
                print(f"      → Expected error caught: {str(e)[:60]}...")
            else:
                print(f"   ✗ Unexpected error on record {i + 1}: {str(e)[:60]}...")

    conn.commit()

    print("\n" + "=" * 70)
    print("⛏️  MINING OPERATION COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   Total students generated: {len(students)}")
    print(f"   Successfully inserted: {inserted_count}")
    print(f"   Errors encountered: {error_count}")
    print(f"   Dirty records with errors: {len(dirty_students)}")

    print(f"\n🔍 Dirty record error types:")
    for ds in dirty_students:
        print(f"   - {ds['_error_type']}")

    # Generate sample output
    print("\n📝 Sample Student Records:")
    print("-" * 70)
    for i in range(min(3, len(students))):
        s = students[i]
        print(f"\nStudent {i + 1}:")
        print(f"   Name: {s['name']}")
        print(f"   UUID: {s['student_uuid']}")
        print(f"   Grade: {s['grade_level']}")
        print(f"   Community: {s['community']}")
        print(
            f"   Programs: PBL={s['is_pbl_participant']}, Hawaiian={s['is_hawaiian_language']}, Hula={s['is_hālau_hula']}"
        )

    print("\n📜 Sample Cultural Reflections:")
    print("-" * 70)
    for i in range(3):
        reflection = generate_cultural_reflection()
        print(f"\nReflection {i + 1}:")
        print(f'   "{reflection}"')

    print("\n" + "=" * 70)
    print("✨ The forest now has life. Ready for the Archmage's inspection.")
    print("=" * 70)

    conn.close()


if __name__ == "__main__":
    main()
