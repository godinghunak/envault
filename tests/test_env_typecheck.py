"""Tests for envault.env_typecheck."""

import pytest

from envault.env_typecheck import (
    TypeViolation,
    check_value,
    detect_type,
    typecheck_env,
)


# ---------------------------------------------------------------------------
# detect_type
# ---------------------------------------------------------------------------

def test_detect_type_integer():
    assert detect_type("42") == "int"


def test_detect_type_negative_integer():
    assert detect_type("-7") == "int"


def test_detect_type_float():
    assert detect_type("3.14") == "float"


def test_detect_type_bool_true():
    assert detect_type("true") == "bool"


def test_detect_type_bool_false():
    assert detect_type("false") == "bool"


def test_detect_type_url():
    assert detect_type("https://example.com") == "url"


def test_detect_type_email():
    assert detect_type("user@example.com") == "email"


def test_detect_type_uuid():
    assert detect_type("550e8400-e29b-41d4-a716-446655440000") == "uuid"


def test_detect_type_str():
    assert detect_type("hello world") == "str"


# ---------------------------------------------------------------------------
# check_value
# ---------------------------------------------------------------------------

def test_check_value_int_valid():
    assert check_value("8080", "int") is True


def test_check_value_int_invalid():
    assert check_value("not_a_number", "int") is False


def test_check_value_str_always_valid():
    assert check_value("anything goes", "str") is True


def test_check_value_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown type"):
        check_value("x", "binary")


def test_check_value_url_valid():
    assert check_value("http://localhost:5000", "url") is True


def test_check_value_url_invalid():
    assert check_value("not-a-url", "url") is False


# ---------------------------------------------------------------------------
# typecheck_env
# ---------------------------------------------------------------------------

_ENV = """PORT=8080
DEBUG=true
API_URL=https://api.example.com
SECRET=mysecret
"""


def test_typecheck_env_no_violations():
    schema = {"PORT": "int", "DEBUG": "bool", "API_URL": "url"}
    assert typecheck_env(_ENV, schema) == []


def test_typecheck_env_detects_violation():
    schema = {"PORT": "int", "SECRET": "int"}
    violations = typecheck_env(_ENV, schema)
    assert len(violations) == 1
    assert violations[0].key == "SECRET"
    assert violations[0].expected_type == "int"


def test_typecheck_env_violation_line_number():
    schema = {"DEBUG": "int"}
    violations = typecheck_env(_ENV, schema)
    assert violations[0].line == 2


def test_typecheck_env_ignores_comments_and_blanks():
    text = "# comment\n\nPORT=abc\n"
    violations = typecheck_env(text, {"PORT": "int"})
    assert len(violations) == 1


def test_typecheck_env_violation_str_repr():
    v = TypeViolation(key="PORT", value="abc", expected_type="int", line=3)
    assert "PORT" in str(v)
    assert "int" in str(v)
    assert "3" in str(v)


def test_typecheck_env_unknown_key_ignored():
    schema = {"NONEXISTENT": "int"}
    violations = typecheck_env(_ENV, schema)
    assert violations == []
