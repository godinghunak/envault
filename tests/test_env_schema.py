import pytest
from envault.env_schema import load_schema, validate_env, validate_env_text, SchemaRule


SCHEMA = """
DATABASE_URL required /postgres://.+/ # database connection string
SECRET_KEY required
DEBUG optional /true|false/
"""


def test_load_schema_parses_rules():
    rules = load_schema(SCHEMA)
    assert len(rules) == 3
    assert rules[0].key == "DATABASE_URL"
    assert rules[0].required is True
    assert rules[0].pattern == "postgres://.+"
    assert rules[1].key == "SECRET_KEY"
    assert rules[2].key == "DEBUG"
    assert rules[2].required is False


def test_load_schema_ignores_comments_and_blanks():
    schema = "# comment\n\nKEY required\n"
    rules = load_schema(schema)
    assert len(rules) == 1
    assert rules[0].key == "KEY"


def test_validate_env_all_valid():
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123", "DEBUG": "true"}
    rules = load_schema(SCHEMA)
    violations = validate_env(env, rules)
    assert violations == []


def test_validate_env_missing_required():
    env = {"DATABASE_URL": "postgres://localhost/db"}
    rules = load_schema(SCHEMA)
    violations = validate_env(env, rules)
    keys = [v.key for v in violations]
    assert "SECRET_KEY" in keys


def test_validate_env_pattern_mismatch():
    env = {"DATABASE_URL": "mysql://localhost/db", "SECRET_KEY": "x"}
    rules = load_schema(SCHEMA)
    violations = validate_env(env, rules)
    keys = [v.key for v in violations]
    assert "DATABASE_URL" in keys


def test_validate_env_optional_missing_is_ok():
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc"}
    rules = load_schema(SCHEMA)
    violations = validate_env(env, rules)
    assert all(v.key != "DEBUG" for v in violations)


def test_validate_env_optional_pattern_enforced_when_present():
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc", "DEBUG": "yes"}
    rules = load_schema(SCHEMA)
    violations = validate_env(env, rules)
    keys = [v.key for v in violations]
    assert "DEBUG" in keys


def test_validate_env_text_convenience():
    env_text = "DATABASE_URL=postgres://localhost/db\nSECRET_KEY=secret\n"
    violations = validate_env_text(env_text, SCHEMA)
    assert violations == []


def test_schema_violation_str():
    from envault.env_schema import SchemaViolation
    v = SchemaViolation("MY_KEY", "required key is missing")
    assert "MY_KEY" in str(v)
    assert "required key is missing" in str(v)
