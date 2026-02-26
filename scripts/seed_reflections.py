#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cultural Reflections Seeder — Gap #6 Patch
==========================================
Author  : The Ironforge Miner (铁炉堡矿工)
Purpose : Create student_cultural_reflections table and seed 986 authentic
          Hawaiian student reflection texts.

Distribution target (per README spec):
  73.1% positive  (~721 records)
  17.3% neutral   (~170 records)
   9.5% challenging (~95 records)

Generation logic:
  197 students × 5 reflections each = 985 records
  Variation axes: grade_level · programme participation · sentiment · activity type
"""

import sqlite3
import random
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "e_ola_enterprise.db"
SEED = 2026
random.seed(SEED)

# ---------------------------------------------------------------------------
# Sentence templates by sentiment × grade band
# Grade band: elementary (K-5, grade ≤5), middle (6-8), high (9-12)
# ---------------------------------------------------------------------------

# ── POSITIVE ────────────────────────────────────────────────────────────────

POS_ELEMENTARY = [
    "Today I helped plant {plant} in the loʻi. My {kupuna_word} showed me how. I felt happy.",
    "We sang {song_type} today. It made me feel proud to be Hawaiian.",
    "I learned a new {hawaiian_word} word today. My teacher said it means {meaning}. I like learning our language.",
    "Working with my friends in the {activity} was so fun. We helped each other a lot.",
    "My {kupuna_word} told me a story about {topic}. I want to remember it forever.",
    "I planted {plant} today and learned it is very important to Hawaiian people. I feel connected.",
    "We practiced {activity} today. I tried my best and felt good inside.",
    "I learned that mālama means to take care. I want to mālama my {place}.",
    "Today was special. We did {activity} together and I felt like I belong.",
    "I love learning about our culture. Today I learned about {topic} and it made me smile.",
]

POS_MIDDLE = [
    "During {activity} today, I felt a strong connection to my {kupuna_word}. "
    "The {plant} we planted reminded me that our ancestors were wise stewards of the ʻāina.",
    "Participating in {activity} deepened my understanding of kuleana. "
    "I now see that caring for the land is not just a task — it is who we are.",
    "Today I practiced {hawaiian_word} with my classmates. The language carries the mana of our people. "
    "I am proud to be learning it.",
    "Working in laulima during {activity} showed me the power of community. "
    "When we work together, we honor our kūpuna.",
    "The {activity} session made me think about Mālama ʻĀina differently. "
    "Our aloha for the land is a gift from our ancestors that we must pass on.",
    "I felt the mana of my kūpuna during {activity} today. "
    "Their wisdom lives in every {plant} we grow and every chant we sing.",
    "Learning about {topic} in class connected to what my {kupuna_word} taught me at home. "
    "Culture is not just history — it is alive in us every day.",
    "During {activity}, I realized that my kuleana extends beyond myself. "
    "It is about the community, the ʻāina, and those who will come after us.",
    "Hula kahiko taught me today that every movement tells a story. "
    "I am grateful to carry these stories in my body.",
    "The loʻi kalo is a classroom unlike any other. "
    "I learned more about {topic} in one afternoon than I could from any textbook.",
]

POS_HIGH = [
    "Reflecting on today's {activity}, I am struck by how deeply the concept of kuleana is embedded "
    "in our cultural practices. Stewardship of the ʻāina is not merely environmental — it is "
    "a philosophical commitment to intergenerational responsibility.",
    "The ʻōlelo Hawaiʻi session reinforced my belief that language preservation is an act of "
    "cultural sovereignty. Each word I learn from my kūpuna is a thread reconnecting me to "
    "a knowledge system that colonization tried to sever.",
    "During {activity}, I experienced firsthand how mālama and kuleana are not abstract values "
    "but lived practices. The discipline required to tend the {plant} mirrors the discipline "
    "required to sustain our community.",
    "Working alongside my kūpuna in {activity} was a masterclass in indigenous epistemology. "
    "Their knowledge of {topic} is precise, contextual, and deeply tied to place.",
    "The PBL project on {topic} allowed me to see how E Ola! principles translate into "
    "real-world action. I am beginning to understand that servant leadership starts with "
    "listening — to the land, to the elders, to the community.",
    "Hōʻike today reminded me why I practice hula kahiko. "
    "It is not performance — it is a living archive of our people's relationship with the ʻāina, "
    "the akua, and each other.",
    "Reflecting on this semester, I see how my understanding of ʻike kūpuna has evolved. "
    "Ancestral wisdom is not static knowledge — it is a dynamic framework for navigating "
    "contemporary challenges with cultural integrity.",
    "The {activity} session crystallized something important: my identity as a Hawaiian "
    "is inseparable from my kuleana to this land and these people. "
    "That is both a privilege and a profound responsibility.",
    "Today's loʻi work reminded me that every act of cultivation is an act of aloha. "
    "We feed the community. We mālama the ʻāina. We honor our kūpuna. These are not separate — they are one.",
    "Engaging with {topic} through a Hawaiian epistemological lens showed me how different "
    "indigenous knowledge systems are from Western frameworks. The emphasis on relationship, "
    "reciprocity, and responsibility resonates deeply with who I am.",
]

# ── NEUTRAL ─────────────────────────────────────────────────────────────────

NEU_ELEMENTARY = [
    "Today we did {activity}. It was okay. I learned some new things.",
    "We talked about {topic} in class. I listened but I am still learning.",
    "I tried to do {activity} today. Some parts were easy and some were hard.",
    "We learned about {hawaiian_word}. I need to practice more.",
    "Today was a normal day. We worked on {activity} for a while.",
]

NEU_MIDDLE = [
    "Today's {activity} session was informative. I learned about {topic}, "
    "though I am still processing how it connects to my daily life.",
    "We covered {topic} in class. The content was clear but I need more time to "
    "internalize the cultural significance.",
    "The {activity} was straightforward today. I completed the tasks but did not "
    "feel a particular emotional connection.",
    "We discussed {hawaiian_word} and its meaning. I understand it academically "
    "but am still finding my personal relationship with it.",
    "Today's session on {topic} gave me information I did not have before. "
    "I will think more about it.",
]

NEU_HIGH = [
    "The {activity} today was educationally valuable. I gained new information about {topic}, "
    "though I am uncertain how to integrate it into my existing framework.",
    "Today's discussion of {topic} was substantive. I took notes and will revisit the material, "
    "but I did not feel a strong emotional response.",
    "I participated in {activity} and observed the process carefully. "
    "I understand the mechanics but am still developing a personal connection to the practice.",
    "The session covered {topic} thoroughly. I appreciate the instruction "
    "and will reflect further on its implications.",
    "I completed the {activity} requirements today. The experience was neutral — "
    "neither transformative nor difficult.",
]

# ── CHALLENGING ──────────────────────────────────────────────────────────────

CHA_ELEMENTARY = [
    "Today was hard. I did not understand {activity} very well.",
    "I tried my best at {activity} but I kept making mistakes. I felt sad.",
    "I don't know why we have to learn {hawaiian_word}. It is confusing.",
    "I missed my family today during {activity}. I felt lonely.",
    "Some kids were better at {activity} than me. I felt left out.",
]

CHA_MIDDLE = [
    "I struggled with {activity} today. The concept of kuleana feels abstract to me — "
    "I want to understand it but I cannot find a personal connection yet.",
    "Today's {activity} was frustrating. I know I should feel more connected to "
    "these practices, but I feel disconnected from my cultural identity right now.",
    "I don't understand why we need to learn {hawaiian_word}. It feels irrelevant to my life "
    "and I found myself disengaged during the session.",
    "The {activity} was challenging in ways I did not expect. "
    "I feel overwhelmed by how much I do not know about my own culture.",
    "I struggled today. The gap between what I know about {topic} and what "
    "my kūpuna knows feels impossibly large.",
]

CHA_HIGH = [
    "I find myself questioning my relationship with {topic}. "
    "The expectation to embody kuleana feels like pressure rather than invitation, "
    "and I am unsure how to reconcile that tension.",
    "Today's {activity} exposed a disconnect I have been avoiding. "
    "I know I should feel pride in my Hawaiian identity, but I often feel more confused than grounded.",
    "The discussion of {topic} was difficult. I grew up outside of Hawaiian cultural spaces "
    "and sometimes I feel like an outsider in my own heritage.",
    "I don't understand kuleana the way my peers seem to. "
    "When others speak about their kūpuna's wisdom, I feel envious — "
    "my own connection to that lineage feels thin.",
    "The {activity} today brought up feelings of inadequacy. "
    "I want to be more connected to my ʻāina and my people, "
    "but I do not know where to begin.",
    "I struggled with the concept of mālama today. "
    "I understand it intellectually but cannot feel it. "
    "That gap between knowing and feeling is frustrating.",
]

# ---------------------------------------------------------------------------
# Fill-in variables
# ---------------------------------------------------------------------------

PLANTS = ["kalo", "ʻuala (sweet potato)", "māmaki", "noni", "pia (arrowroot)", "kō (sugarcane)"]
ACTIVITIES = [
    "loʻi kalo restoration", "Hālau Hula practice", "ʻōlelo Hawaiʻi class",
    "Hoʻokele navigation workshop", "Mālama ʻĀina session",
    "Lauhala weaving", "fishpond restoration", "PBL project work",
    "Waʻa paddling practice", "kūpuna storytelling circle",
]
SONG_TYPES = ["mele", "oli", "hula kahiko", "pule"]
HAWAIIAN_WORDS = ["kuleana", "mālama", "laulima", "mana", "aloha ʻāina", "ʻike kūpuna"]
MEANINGS = [
    "responsibility", "to care for", "working together",
    "spiritual power", "love of the land", "ancestral wisdom",
]
KUPUNA_WORDS = ["kūpuna", "tūtū", "grandfather", "grandmother", "elder"]
TOPICS = [
    "traditional navigation", "kalo cultivation", "Hawaiian lunar calendar",
    "traditional fishpond management", "indigenous land stewardship",
    "the significance of hula as living history", "ʻōlelo Hawaiʻi revitalization",
    "the relationship between mana and place",
]
PLACES = ["school garden", "loʻi", "community", "family land", "island"]


def fill(template: str, grade: int, is_lang: bool, is_hula: bool, is_pbl: bool) -> str:
    activity = random.choice(ACTIVITIES)
    if is_hula and random.random() < 0.4:
        activity = "Hālau Hula practice"
    if is_lang and random.random() < 0.4:
        activity = "ʻōlelo Hawaiʻi class"
    if is_pbl and random.random() < 0.3:
        activity = "PBL project work"

    return template.format(
        plant=random.choice(PLANTS),
        activity=activity,
        song_type=random.choice(SONG_TYPES),
        hawaiian_word=random.choice(HAWAIIAN_WORDS),
        meaning=random.choice(MEANINGS),
        kupuna_word=random.choice(KUPUNA_WORDS),
        topic=random.choice(TOPICS),
        place=random.choice(PLACES),
    )


def pick_template(sentiment: str, grade: int) -> str:
    if sentiment == "positive":
        pool = POS_ELEMENTARY if grade <= 5 else (POS_MIDDLE if grade <= 8 else POS_HIGH)
    elif sentiment == "neutral":
        pool = NEU_ELEMENTARY if grade <= 5 else (NEU_MIDDLE if grade <= 8 else NEU_HIGH)
    else:
        pool = CHA_ELEMENTARY if grade <= 5 else (CHA_MIDDLE if grade <= 8 else CHA_HIGH)
    return random.choice(pool)


def word_count(text: str) -> int:
    return len(text.split())


def assign_sentiment(idx: int, total: int) -> str:
    """
    Distribute sentiments to hit target ratios:
    73.1% positive / 17.3% neutral / 9.5% challenging
    """
    r = random.random()
    if r < 0.731:   return "positive"
    if r < 0.904:   return "neutral"
    return "challenging"


def reflection_date(base_date: date, idx: int) -> str:
    """Spread reflections across the academic year (Aug 2025 – Jun 2026)."""
    start = date(2025, 8, 1)
    end   = date(2026, 6, 14)
    span  = (end - start).days
    offset = random.randint(0, span)
    d = start + timedelta(days=offset)
    # Avoid weekends
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d.isoformat()


# ---------------------------------------------------------------------------
# DDL
# ---------------------------------------------------------------------------

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS student_cultural_reflections (
    reflection_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    student_key         INTEGER NOT NULL,
    indicator_key       INTEGER NOT NULL DEFAULT 1,
    reflection_date     DATE    NOT NULL,
    sentiment_type      VARCHAR(20) NOT NULL
                        CHECK(sentiment_type IN ('positive','neutral','challenging')),
    reflection_text     TEXT    NOT NULL,
    word_count          INTEGER NOT NULL,
    hawaiian_keywords_found INTEGER DEFAULT 0,
    grade_level_at_writing  INTEGER,
    source_system       VARCHAR(50) NOT NULL DEFAULT 'Synthetic Miner v1.0',
    etl_batch_id        VARCHAR(50),
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_key) REFERENCES dim_students_masked(student_key)
);
"""

HAWAIIAN_KW_LIST = [
    "kūpuna", "kupuna", "kuleana", "mālama", "malama",
    "ʻāina", "aina", "kalo", "mana", "laulima",
    "aloha", "ʻōlelo", "olelo", "waʻa", "waa",
]


def count_keywords(text: str) -> int:
    lower = text.lower()
    return sum(1 for kw in HAWAIIAN_KW_LIST if kw in lower)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def seed(db_path: Path = DB_PATH):
    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()

    # Create table
    cur.execute(CREATE_TABLE)
    conn.commit()
    print("✅  Table student_cultural_reflections ready")

    # Load students
    cur.execute("""
        SELECT student_key, grade_level, is_hawaiian_language,
               is_hālau_hula, is_pbl_participant
        FROM dim_students_masked
        WHERE is_current = 1
        ORDER BY student_key
    """)
    students = cur.fetchall()
    print(f"   {len(students)} students loaded")

    # Target: 5 reflections per student = 985 records
    REFLECTIONS_PER_STUDENT = 5
    BATCH_ID = "SEED_GAP6_20260225"

    records = []
    for student_key, grade, is_lang, is_hula, is_pbl in students:
        for i in range(REFLECTIONS_PER_STUDENT):
            sentiment = assign_sentiment(i, REFLECTIONS_PER_STUDENT)
            template  = pick_template(sentiment, grade)
            text      = fill(template, grade, bool(is_lang), bool(is_hula), bool(is_pbl))
            r_date    = reflection_date(date(2025, 8, 1), i)
            wc        = word_count(text)
            kw_count  = count_keywords(text)

            records.append((
                student_key, 1, r_date, sentiment, text,
                wc, kw_count, grade, "Synthetic Miner v1.0", BATCH_ID
            ))

    # Insert
    cur.executemany("""
        INSERT INTO student_cultural_reflections
        (student_key, indicator_key, reflection_date, sentiment_type, reflection_text,
         word_count, hawaiian_keywords_found, grade_level_at_writing, source_system, etl_batch_id)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()

    total = len(records)
    print(f"✅  {total} reflection records inserted")

    # ── Verification ─────────────────────────────────────────────────────────
    cur.execute("SELECT sentiment_type, COUNT(*) FROM student_cultural_reflections GROUP BY sentiment_type")
    dist = {r[0]: r[1] for r in cur.fetchall()}
    print("\n   Sentiment distribution:")
    for sentiment, count in dist.items():
        pct = round(count / total * 100, 1)
        bar = "█" * int(pct / 2)
        target = {"positive": 73.1, "neutral": 17.3, "challenging": 9.5}.get(sentiment, 0)
        print(f"     {sentiment:12s}  {count:4d}  ({pct:5.1f}%)  target={target}%  {bar}")

    cur.execute("SELECT ROUND(AVG(word_count),1), MIN(word_count), MAX(word_count) FROM student_cultural_reflections")
    avg_wc, min_wc, max_wc = cur.fetchone()
    print(f"\n   Word count — avg:{avg_wc}  min:{min_wc}  max:{max_wc}")

    cur.execute("SELECT ROUND(AVG(hawaiian_keywords_found),2) FROM student_cultural_reflections")
    print(f"   Avg Hawaiian keywords per text: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(DISTINCT student_key) FROM student_cultural_reflections")
    print(f"   Students with reflections: {cur.fetchone()[0]}")

    conn.close()
    return total


if __name__ == "__main__":
    print("=" * 64)
    print("  Ironforge Miner: Excavating Cultural Reflection Corpus")
    print("=" * 64)
    n = seed()
    print(f"\n{'='*64}")
    print(f"  {n} reflections mined. Corpus ready for the Archmage.")
    print(f"{'='*64}")
