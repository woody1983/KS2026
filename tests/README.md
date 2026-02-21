# E Ola! Testing Framework

## Overview

The Night's Watch has established a comprehensive TDD framework for the E Ola! Learner Analytics System.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and helpers
├── unit/
│   ├── test_schema.py            # Database schema validation
│   └── test_constraints.py       # FK, CHECK constraints, DDM
└── integration/
    └── test_data_pipeline.py     # End-to-end data flow tests
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
# Unit tests only
pytest -m unit

# Integration tests (requires database)
pytest -m integration

# Schema validation
pytest -m schema

# DDM (privacy) tests
pytest -m ddm
```

### Run with coverage
```bash
pytest --cov=scripts --cov-report=html
```

## Test Categories

### Schema Tests (`test_schema.py`)
- ✅ All expected tables exist
- ✅ All expected views exist
- ✅ SCD Type 2 support (valid_from, valid_to, is_current)
- ✅ Audit fields on all tables (created_at, updated_at)
- ✅ Foreign key constraints
- ✅ Index creation

### Constraint Tests (`test_constraints.py`)
- ✅ Foreign key violation detection
- ✅ Data quality constraints (score ranges)
- ✅ Dynamic Data Masking (DDM) views
- ✅ PII isolation compliance
- ✅ Audit trail validation
- ✅ SCD Type 2 versioning

### Integration Tests (`test_data_pipeline.py`)
- ✅ Complete data flow (mapping → masked → outcomes)
- ✅ Cascade delete restrictions
- ✅ Bulk insert performance

## Key Testing Principles

1. **Isolation**: Each test uses fresh in-memory database
2. **Fixtures**: Shared test data via `conftest.py`
3. **Markers**: Categorize tests for selective execution
4. **Coverage**: Track code coverage with pytest-cov

## Database Test Helper

The `DatabaseTestHelper` class provides:
- Connection management
- Schema introspection
- Constraint validation
- Transaction control

## FERPA Compliance Testing

- PII isolation in `dim_student_mapping`
- DDM views for different user roles
- Cell-size suppression for researcher views
- Audit trail validation
