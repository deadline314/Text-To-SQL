"""Tests for configuration."""

from config import DB_CONFIG, FULL_SCHEMA


def test_db_config_has_required_fields():
    assert DB_CONFIG.host is not None
    assert DB_CONFIG.port == 0000
    assert DB_CONFIG.user is not None
    assert DB_CONFIG.password is not None


def test_full_schema_contains_all_tables():
    assert "tencent_bill" in FULL_SCHEMA
    assert "global_bill" in FULL_SCHEMA
    assert "global_bill_l3" in FULL_SCHEMA


def test_schema_contains_comments():
    assert "COMMENT" in FULL_SCHEMA
    assert "騰訊" in FULL_SCHEMA or "tencent" in FULL_SCHEMA.lower()
