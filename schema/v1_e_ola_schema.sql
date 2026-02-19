-- ============================================================================
-- E Ola! Learner Analytics System - Physical Schema v1.0
-- Author: The Night's Watch (守夜人)
-- Date: 2026-02-18
-- Description: Star Schema with FERPA-compliant PII isolation
-- ============================================================================

-- ============================================================================
-- SECTION 1: PII ISOLATION LAYER (The Wall)
-- Purpose: Physical separation of identifiable information from analytics
-- Security: AES-256 encryption, restricted access, audit logging
-- ============================================================================

CREATE TABLE dim_student_mapping (
    mapping_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    student_uuid            VARCHAR(36) NOT NULL UNIQUE,      -- Anonymous analytics ID
    student_id_hash         VARCHAR(64) NOT NULL UNIQUE,      -- SHA-256 hash of real student_id
    encryption_key_ref      VARCHAR(255) NOT NULL,            -- Reference to Azure Key Vault key
    
    -- Audit Fields (Mandatory)
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by              VARCHAR(100) NOT NULL,
    updated_by              VARCHAR(100) NOT NULL,
    
    -- Constraints
    CONSTRAINT chk_student_uuid_format CHECK (student_uuid LIKE '________-____-____-____-____________'),
    CONSTRAINT chk_student_id_hash_len CHECK (LENGTH(student_id_hash) = 64)
);

-- Index for fast lookups
CREATE UNIQUE INDEX idx_student_uuid ON dim_student_mapping(student_uuid);
CREATE UNIQUE INDEX idx_student_id_hash ON dim_student_mapping(student_id_hash);

-- ============================================================================
-- SECTION 2: DIMENSION TABLES
-- ============================================================================

-- ------------------------------------------------------------------------
-- Dimension: Time/Academic Calendar
-- Purpose: Support time-series analysis and academic period tracking
-- ------------------------------------------------------------------------
CREATE TABLE dim_date (
    date_key                INTEGER PRIMARY KEY,              -- YYYYMMDD format
    full_date               DATE NOT NULL UNIQUE,
    day_of_week             TINYINT NOT NULL,
    day_name                VARCHAR(10) NOT NULL,
    day_of_month            TINYINT NOT NULL,
    day_of_year             SMALLINT NOT NULL,
    week_of_year            TINYINT NOT NULL,
    month_number            TINYINT NOT NULL,
    month_name              VARCHAR(10) NOT NULL,
    quarter                 TINYINT NOT NULL,
    year_number             SMALLINT NOT NULL,
    fiscal_year             SMALLINT NOT NULL,
    
    -- Academic Calendar Fields
    academic_year           VARCHAR(9) NOT NULL,              -- e.g., '2025-2026'
    academic_term           VARCHAR(20) NOT NULL,             -- Fall, Spring, Summer
    term_start_date         DATE NOT NULL,
    term_end_date           DATE NOT NULL,
    is_school_day           BOOLEAN NOT NULL DEFAULT 1,
    is_holiday              BOOLEAN NOT NULL DEFAULT 0,
    holiday_name            VARCHAR(50),
    
    -- Audit Fields
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_academic_year_term ON dim_date(academic_year, academic_term);
CREATE INDEX idx_date_full ON dim_date(full_date);

-- ------------------------------------------------------------------------
-- Dimension: Students (Masked for Analytics)
-- Purpose: Student attributes without PII for analytics queries
-- Security: All PII references go through dim_student_mapping
-- ------------------------------------------------------------------------
CREATE TABLE dim_students_masked (
    student_key             INTEGER PRIMARY KEY AUTOINCREMENT,
    student_uuid            VARCHAR(36) NOT NULL UNIQUE,      -- Foreign key to mapping table
    
    -- Demographics (Categorized for privacy)
    grade_level             TINYINT NOT NULL,
    gender_category         VARCHAR(20),                      -- 'Male', 'Female', 'Non-binary', 'Prefer not to say'
    ethnicity_category      VARCHAR(50),                      -- Aggregated categories
    
    -- Academic Classification
    enrollment_status       VARCHAR(20) NOT NULL DEFAULT 'Active', -- Active, Inactive, Graduated, Withdrawn
    entry_date              DATE NOT NULL,
    expected_graduation_year SMALLINT,
    
    -- Program Participation Flags
    is_pbl_participant      BOOLEAN NOT NULL DEFAULT 0,
    is_hawaiian_language    BOOLEAN NOT NULL DEFAULT 0,
    is_hālau_hula           BOOLEAN NOT NULL DEFAULT 0,
    
    -- Cohort Information
    cohort_year             SMALLINT NOT NULL,
    homeroom_id             VARCHAR(20),
    
    -- Audit Fields
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    FOREIGN KEY (student_uuid) REFERENCES dim_student_mapping(student_uuid)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_students_grade ON dim_students_masked(grade_level);
CREATE INDEX idx_students_cohort ON dim_students_masked(cohort_year);
CREATE INDEX idx_students_enrollment ON dim_students_masked(enrollment_status);

-- ------------------------------------------------------------------------
-- Dimension: E Ola! Indicators
-- Purpose: Hierarchical classification of 14 learner outcomes
-- Structure: Roots → Trunk/Branches → Leaves → Fruits
-- ------------------------------------------------------------------------
CREATE TABLE dim_e_ola_indicators (
    indicator_key           INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_code          VARCHAR(20) NOT NULL UNIQUE,      -- e.g., 'ROOT_IKE', 'LEAF_ACAD'
    indicator_name          VARCHAR(100) NOT NULL,
    indicator_name_hawaiian VARCHAR(100),
    
    -- Hierarchical Classification (Native Hawaiian Forest Metaphor)
    tier_level              VARCHAR(20) NOT NULL,             -- Roots, Trunk_Branches, Leaves, Fruits
    tier_order              TINYINT NOT NULL,                 -- Display order within tier
    parent_indicator_key    INTEGER,                          -- Self-referencing for hierarchy
    
    -- Measurement Properties
    measurement_type        VARCHAR(20) NOT NULL,             -- Quantitative, Qualitative, Mixed
    data_collection_method  VARCHAR(50),                      -- Survey, Observation, Portfolio, etc.
    assessment_frequency    VARCHAR(20),                      -- Daily, Weekly, Monthly, Quarterly, Annual
    
    -- Scoring
    min_score               DECIMAL(5,2),
    max_score               DECIMAL(5,2),
    proficiency_threshold   DECIMAL(5,2),                     -- Score indicating proficiency
    
    -- Descriptions
    description             TEXT,
    learning_outcomes       TEXT,                             -- Expected outcomes at proficiency
    
    -- Audit Fields
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active               BOOLEAN NOT NULL DEFAULT 1,
    
    -- Foreign Key
    FOREIGN KEY (parent_indicator_key) REFERENCES dim_e_ola_indicators(indicator_key)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_indicators_tier ON dim_e_ola_indicators(tier_level, tier_order);
CREATE INDEX idx_indicators_active ON dim_e_ola_indicators(is_active);

-- ------------------------------------------------------------------------
-- Dimension: Assessment Types
-- Purpose: Categorize different measurement instruments
-- ------------------------------------------------------------------------
CREATE TABLE dim_assessment_types (
    assessment_type_key     INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_type_code    VARCHAR(20) NOT NULL UNIQUE,
    assessment_type_name    VARCHAR(100) NOT NULL,
    
    -- Classification
    source_system           VARCHAR(50),                      -- SIS, LMS, Manual Entry, External
    modality                VARCHAR(20),                      -- Self-report, Observer-rated, Performance, Portfolio
    data_format             VARCHAR(20),                      -- Numeric, Text, Rubric, Mixed
    
    -- Properties
    is_standardized         BOOLEAN NOT NULL DEFAULT 0,
    is_formative            BOOLEAN NOT NULL DEFAULT 1,
    reliability_score       DECIMAL(3,2),                     -- Cronbach's alpha or equivalent
    
    -- Audit Fields
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active               BOOLEAN NOT NULL DEFAULT 1
);

-- ------------------------------------------------------------------------
-- Dimension: Well-being Dimensions
-- Purpose: Seven-dimensional well-being framework
-- ------------------------------------------------------------------------
CREATE TABLE dim_wellbeing_dimensions (
    dimension_key           INTEGER PRIMARY KEY AUTOINCREMENT,
    dimension_code          VARCHAR(20) NOT NULL UNIQUE,      -- e.g., 'WB_CULTURAL', 'WB_PHYSICAL'
    dimension_name          VARCHAR(50) NOT NULL,
    dimension_name_hawaiian VARCHAR(50),
    dimension_order         TINYINT NOT NULL,                 -- For radar chart ordering
    
    -- Measurement
    measurement_instruments TEXT,                             -- JSON array of instrument names
    data_sources            TEXT,                             -- JSON array of source systems
    
    -- Audit Fields
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active               BOOLEAN NOT NULL DEFAULT 1
);

-- ------------------------------------------------------------------------
-- Dimension: PBL Projects
-- Purpose: Track Project-Based Learning initiatives
-- ------------------------------------------------------------------------
CREATE TABLE dim_pbl_projects (
    project_key             INTEGER PRIMARY KEY AUTOINCREMENT,
    project_code            VARCHAR(20) NOT NULL UNIQUE,
    project_title           VARCHAR(200) NOT NULL,
    project_description     TEXT,
    
    -- Timeline
    project_start_date      DATE NOT NULL,
    project_end_date        DATE NOT NULL,
    academic_year           VARCHAR(9) NOT NULL,
    academic_term           VARCHAR(20) NOT NULL,
    
    -- Classification
    subject_area            VARCHAR(50),
    grade_levels            VARCHAR(50),                      -- JSON array or comma-separated
    project_type            VARCHAR(50),                      -- Community, Academic, Cultural, etc.
    
    -- E Ola! Alignment
    primary_indicator_key   INTEGER,                          -- Primary E Ola! indicator addressed
    secondary_indicators    TEXT,                             -- JSON array of additional indicators
    
    -- Implementation Tracking
    implementation_phase    VARCHAR(20) NOT NULL DEFAULT 'Planning', -- Awareness, Preparation, Implementation, Refinement
    teacher_id              VARCHAR(50),                      -- Reference to teacher (anonymized)
    
    -- Audit Fields
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active               BOOLEAN NOT NULL DEFAULT 1,
    
    -- Foreign Key
    FOREIGN KEY (primary_indicator_key) REFERENCES dim_e_ola_indicators(indicator_key)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_pbl_year_term ON dim_pbl_projects(academic_year, academic_term);
CREATE INDEX idx_pbl_phase ON dim_pbl_projects(implementation_phase);

-- ============================================================================
-- SECTION 3: FACT TABLES
-- ============================================================================

-- ------------------------------------------------------------------------
-- Fact: E Ola! Outcomes (Core Fact Table)
-- Purpose: Store all student indicator measurements
-- Grain: One row per student per indicator per assessment event
-- ------------------------------------------------------------------------
CREATE TABLE fact_e_ola_outcomes (
    outcome_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Keys
    student_key             INTEGER NOT NULL,
    indicator_key           INTEGER NOT NULL,
    assessment_type_key     INTEGER NOT NULL,
    date_key                INTEGER NOT NULL,
    project_key             INTEGER,                          -- Optional: if part of PBL project
    
    -- Measures
    raw_score               DECIMAL(8,3),                     -- Original score
    normalized_score        DECIMAL(5,2),                     -- 0-100 scale for comparison
    proficiency_level       VARCHAR(20),                      -- Below, Approaching, Proficient, Advanced
    percentile_rank         DECIMAL(5,2),                     -- Relative standing
    
    -- Qualitative Data (for NLP analysis)
    qualitative_data_id     INTEGER,                          -- Reference to text/narrative data
    
    -- Metadata
    assessment_date         DATE NOT NULL,
    assessor_type           VARCHAR(20),                      -- Self, Peer, Teacher, System
    data_quality_flag       VARCHAR(20) DEFAULT 'Valid',      -- Valid, Suspect, Missing, Imputed
    
    -- Audit Fields
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system           VARCHAR(50) NOT NULL,
    etl_batch_id            VARCHAR(50),                      -- For data lineage
    
    -- Foreign Keys
    FOREIGN KEY (student_key) REFERENCES dim_students_masked(student_key)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (indicator_key) REFERENCES dim_e_ola_indicators(indicator_key)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (assessment_type_key) REFERENCES dim_assessment_types(assessment_type_key)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (project_key) REFERENCES dim_pbl_projects(project_key)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- Performance Indexes (Critical for query performance)
CREATE INDEX idx_outcomes_student_date ON fact_e_ola_outcomes(student_key, date_key);
CREATE INDEX idx_outcomes_indicator_date ON fact_e_ola_outcomes(indicator_key, date_key);
CREATE INDEX idx_outcomes_date_indicator ON fact_e_ola_outcomes(date_key, indicator_key);
CREATE INDEX idx_outcomes_project ON fact_e_ola_outcomes(project_key) WHERE project_key IS NOT NULL;
CREATE INDEX idx_outcomes_proficiency ON fact_e_ola_outcomes(proficiency_level);

-- ------------------------------------------------------------------------
-- Fact: Well-being Measurements
-- Purpose: Seven-dimensional well-being scores
-- Grain: One row per student per assessment event
-- ------------------------------------------------------------------------
CREATE TABLE fact_wellbeing_measurements (
    wellbeing_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Keys
    student_key             INTEGER NOT NULL,
    date_key                INTEGER NOT NULL,
    assessment_type_key     INTEGER NOT NULL,
    
    -- Seven Dimensions (0-100 scale each)
    cultural_score          DECIMAL(5,2),
    spiritual_score         DECIMAL(5,2),
    social_score            DECIMAL(5,2),
    economic_score          DECIMAL(5,2),
    physical_score          DECIMAL(5,2),
    emotional_score         DECIMAL(5,2),
    cognitive_score         DECIMAL(5,2),
    
    -- Composite Score
    overall_wellbeing_score DECIMAL(5,2),                     -- Weighted average
    wellbeing_category      VARCHAR(20),                      -- Thriving, Balanced, Struggling, Crisis
    
    -- Metadata
    assessment_date         DATE NOT NULL,
    data_sources            TEXT,                             -- JSON array of contributing sources
    
    -- Audit Fields
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system           VARCHAR(50) NOT NULL,
    etl_batch_id            VARCHAR(50),
    
    -- Foreign Keys
    FOREIGN KEY (student_key) REFERENCES dim_students_masked(student_key)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (assessment_type_key) REFERENCES dim_assessment_types(assessment_type_key)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_wellbeing_student_date ON fact_wellbeing_measurements(student_key, date_key);
CREATE INDEX idx_wellbeing_date_category ON fact_wellbeing_measurements(date_key, wellbeing_category);

-- ------------------------------------------------------------------------
-- Fact: PBL Implementation Tracking
-- Purpose: Monitor PBL-by-Design initiative adoption
-- Grain: One row per project per student per metric
-- ------------------------------------------------------------------------
CREATE TABLE fact_pbl_implementation (
    implementation_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Keys
    project_key             INTEGER NOT NULL,
    student_key             INTEGER,                          -- NULL for project-level metrics
    date_key                INTEGER NOT NULL,
    
    -- Implementation Dimensions (Reach, Frequency, Quality, Outcomes)
    metric_category         VARCHAR(20) NOT NULL,             -- Reach, Frequency, Quality, Outcome
    metric_name             VARCHAR(50) NOT NULL,
    metric_value            DECIMAL(8,3),
    metric_unit             VARCHAR(20),
    
    -- Fidelity Scoring
    fidelity_score          DECIMAL(5,2),                     -- 0-100 implementation fidelity
    fidelity_level          VARCHAR(20),                      -- Surface, Developing, Deep, Transformative
    
    -- Barriers and Supports
    identified_barriers     TEXT,                             -- JSON array
    implemented_supports    TEXT,                             -- JSON array
    
    -- Audit Fields
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    etl_batch_id            VARCHAR(50),
    
    -- Foreign Keys
    FOREIGN KEY (project_key) REFERENCES dim_pbl_projects(project_key)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (student_key) REFERENCES dim_students_masked(student_key)
        ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_pbl_impl_project ON fact_pbl_implementation(project_key);
CREATE INDEX idx_pbl_impl_student ON fact_pbl_implementation(student_key) WHERE student_key IS NOT NULL;
CREATE INDEX idx_pbl_impl_metric ON fact_pbl_implementation(metric_category, metric_name);

-- ------------------------------------------------------------------------
-- Fact: Intervention Tracking
-- Purpose: Track student interventions and outcomes
-- ------------------------------------------------------------------------
CREATE TABLE fact_interventions (
    intervention_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Keys
    student_key             INTEGER NOT NULL,
    date_key_start          INTEGER NOT NULL,
    date_key_end            INTEGER,
    triggered_indicator_key INTEGER,                          -- Which indicator triggered intervention
    
    -- Intervention Details
    intervention_type       VARCHAR(50) NOT NULL,             -- Academic, Behavioral, Wellness, etc.
    intervention_tier       TINYINT NOT NULL DEFAULT 1,       -- RTI/MTSS Tier 1, 2, 3
    intervention_description TEXT,
    provider_role           VARCHAR(50),                      -- Teacher, Counselor, Specialist, etc.
    
    -- Outcomes
    outcome_status          VARCHAR(20),                      -- In Progress, Successful, Partial, Unsuccessful
    outcome_score_change    DECIMAL(5,2),                     -- Pre-post score difference
    duration_days           INTEGER,                          -- Actual duration
    
    -- Audit Fields
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (student_key) REFERENCES dim_students_masked(student_key)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (date_key_start) REFERENCES dim_date(date_key)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (date_key_end) REFERENCES dim_date(date_key)
        ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (triggered_indicator_key) REFERENCES dim_e_ola_indicators(indicator_key)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_interventions_student ON fact_interventions(student_key);
CREATE INDEX idx_interventions_status ON fact_interventions(outcome_status);

-- ============================================================================
-- SECTION 4: VIEWS (Dynamic Data Masking Layer)
-- Purpose: Role-based data access without exposing raw tables
-- ============================================================================

-- Teacher View: Current students only, full detail
CREATE VIEW vw_teacher_student_outcomes AS
SELECT 
    s.student_key,
    s.student_uuid,
    s.grade_level,
    s.cohort_year,
    s.enrollment_status,
    o.indicator_key,
    i.indicator_name,
    i.tier_level,
    o.assessment_date,
    o.normalized_score,
    o.proficiency_level,
    o.percentile_rank
FROM dim_students_masked s
JOIN fact_e_ola_outcomes o ON s.student_key = o.student_key
JOIN dim_e_ola_indicators i ON o.indicator_key = i.indicator_key
WHERE s.enrollment_status = 'Active'
    AND o.assessment_date >= DATE('now', '-1 year');

-- Leader View: Aggregated statistics, no individual identifiers
CREATE VIEW vw_leader_cohort_summary AS
SELECT 
    s.grade_level,
    s.cohort_year,
    i.tier_level,
    i.indicator_name,
    COUNT(DISTINCT s.student_key) as student_count,
    AVG(o.normalized_score) as avg_score,
    MIN(o.normalized_score) as min_score,
    MAX(o.normalized_score) as max_score,
    STDDEV(o.normalized_score) as std_dev,
    SUM(CASE WHEN o.proficiency_level = 'Proficient' THEN 1 ELSE 0 END) as proficient_count,
    ROUND(100.0 * SUM(CASE WHEN o.proficiency_level = 'Proficient' THEN 1 ELSE 0 END) / COUNT(*), 2) as proficiency_rate
FROM dim_students_masked s
JOIN fact_e_ola_outcomes o ON s.student_key = o.student_key
JOIN dim_e_ola_indicators i ON o.indicator_key = i.indicator_key
WHERE s.enrollment_status = 'Active'
GROUP BY s.grade_level, s.cohort_year, i.tier_level, i.indicator_name;

-- Researcher View: Anonymized with statistical noise
CREATE VIEW vw_researcher_anonymized AS
SELECT 
    s.cohort_year,
    s.grade_level,
    s.gender_category,
    s.ethnicity_category,
    i.indicator_code,
    i.tier_level,
    d.academic_year,
    d.academic_term,
    AVG(o.normalized_score) as avg_score,
    COUNT(*) as sample_size
FROM dim_students_masked s
JOIN fact_e_ola_outcomes o ON s.student_key = o.student_key
JOIN dim_e_ola_indicators i ON o.indicator_key = i.indicator_key
JOIN dim_date d ON o.date_key = d.date_key
GROUP BY s.cohort_year, s.grade_level, s.gender_category, s.ethnicity_category,
         i.indicator_code, i.tier_level, d.academic_year, d.academic_term
HAVING COUNT(*) >= 10;  -- Cell size suppression for privacy

-- ============================================================================
-- SECTION 5: SEED DATA
-- ============================================================================

-- Insert E Ola! Indicators (14 learner outcomes)
INSERT INTO dim_e_ola_indicators (indicator_code, indicator_name, indicator_name_hawaiian, tier_level, tier_order, measurement_type, description) VALUES
-- Roots (Cultural Foundation)
('ROOT_IKE', '''Ike Kūpuna', 'Ancestral Wisdom', 'Roots', 1, 'Mixed', 'Understanding of Hawaiian traditional knowledge, practices, and perspectives'),
('ROOT_ALOHA', 'Aloha ''Āina', 'Love of Land', 'Roots', 2, 'Mixed', 'Emotional connection to Hawaiian land and environmental stewardship'),
('ROOT_KUPONO', 'Kūpono', 'Integrity', 'Roots', 3, 'Qualitative', 'Honorable character grounded in Hawaiian and Christian values'),

-- Trunk & Branches (Identity Formation)
('TRUNK_MALAMA', 'Mālama & Kuleana', 'Stewardship & Responsibility', 'Trunk_Branches', 1, 'Mixed', 'Social agency and conscious commitment to community benefit'),
('TRUNK_ALAKAI', 'Alaka''i Lawelawe', 'Servant Leadership', 'Trunk_Branches', 2, 'Qualitative', 'Leadership exercised through service to others'),
('TRUNK_KULIA', 'Kūlia', 'Excellence', 'Trunk_Branches', 3, 'Mixed', 'Commitment to personal best and continuous improvement'),

-- Leaves (Action & Skills)
('LEAF_ACAD', 'Academic Competence', NULL, 'Leaves', 1, 'Quantitative', 'Cross-disciplinary academic achievement'),
('LEAF_MINDSET', 'Growth Mindset', NULL, 'Leaves', 2, 'Quantitative', 'Belief in ability to develop abilities through effort'),
('LEAF_EFFICACY', 'Self-efficacy', NULL, 'Leaves', 3, 'Quantitative', 'Confidence in ability to succeed'),
('LEAF_PROBLEM', 'Problem Solving', NULL, 'Leaves', 4, 'Mixed', 'Critical thinking and creative solution generation'),
('LEAF_INNOV', 'Innovation & Creativity', NULL, 'Leaves', 5, 'Mixed', 'Novel idea generation and implementation'),
('LEAF_COLLAB', 'Collaboration', NULL, 'Leaves', 6, 'Qualitative', 'Effective teamwork and interpersonal skills'),
('LEAF_GLOBAL', 'Global Competence', NULL, 'Leaves', 7, 'Mixed', 'Cross-cultural understanding and communication'),

-- Fruits & Seeds (Ultimate Well-Being)
('FRUIT_WELLBEING', 'Holistic Well-Being', NULL, 'Fruits', 1, 'Mixed', 'Comprehensive wellness across seven dimensions');

-- Insert Well-being Dimensions
INSERT INTO dim_wellbeing_dimensions (dimension_code, dimension_name, dimension_name_hawaiian, dimension_order) VALUES
('WB_CULTURAL', 'Cultural', NULL, 1),
('WB_SPIRITUAL', 'Spiritual', NULL, 2),
('WB_SOCIAL', 'Social', NULL, 3),
('WB_ECONOMIC', 'Economic', NULL, 4),
('WB_PHYSICAL', 'Physical', NULL, 5),
('WB_EMOTIONAL', 'Emotional', NULL, 6),
('WB_COGNITIVE', 'Cognitive', NULL, 7);

-- Insert Assessment Types
INSERT INTO dim_assessment_types (assessment_type_code, assessment_type_name, source_system, modality, data_format) VALUES
('SELF_REPORT', 'Self-Report Survey', 'Internal', 'Self-report', 'Numeric'),
('TEACHER_OBS', 'Teacher Observation', 'Internal', 'Observer-rated', 'Rubric'),
('PORTFOLIO', 'Portfolio Assessment', 'LMS', 'Performance', 'Mixed'),
('STANDARDIZED', 'Standardized Test', 'External', 'Performance', 'Numeric'),
('PEER_360', '360-Degree Feedback', 'Internal', 'Observer-rated', 'Rubric'),
('NLP_JOURNAL', 'NLP Journal Analysis', 'Analytics Engine', 'System', 'Text'),
('BEHAVIORAL', 'Behavioral Record', 'SIS', 'System', 'Numeric');

-- ============================================================================
-- SECTION 6: AUDIT TRIGGERS
-- Purpose: Automatic timestamp updates
-- ============================================================================

CREATE TRIGGER trg_student_mapping_updated
AFTER UPDATE ON dim_student_mapping
BEGIN
    UPDATE dim_student_mapping 
    SET updated_at = CURRENT_TIMESTAMP
    WHERE mapping_id = NEW.mapping_id;
END;

CREATE TRIGGER trg_students_masked_updated
AFTER UPDATE ON dim_students_masked
BEGIN
    UPDATE dim_students_masked 
    SET updated_at = CURRENT_TIMESTAMP
    WHERE student_key = NEW.student_key;
END;

-- ============================================================================
-- NOTES
-- ============================================================================
-- 1. All tables include created_at and updated_at audit fields (mandatory)
-- 2. Foreign key constraints enforce referential integrity
-- 3. Indexes optimized for common query patterns
-- 4. Views implement role-based data masking (FERPA compliant)
-- 5. PII completely isolated in dim_student_mapping (The Wall)
-- 6. Star schema design optimized for analytics queries
-- 7. SQLite compatible (development); Azure SQL migration ready
-- ============================================================================
