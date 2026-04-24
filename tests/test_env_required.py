"""Tests for envault.env_required."""

import pytest

from envault.env_required import (
    MissingKeyIssue,
    RequiredCheckResult,
    check_required,
    check_required_from_text,
    format_result,
    load_required_keys,
)


# ---------------------------------------------------------------------------
# load_required_keys
# ---------------------------------------------------------------------------

def test_load_required_keys_basic():
    text = "DB_HOST\nDB_PORT\n"
    keys = load_required_keys(text)
    assert keys == {"DB_HOST", "DB_PORT"}


def test_load_required_keys_ignores_comments():
    text = "# this is a comment\nSECRET_KEY\n"
    keys = load_required_keys(text)
    assert "SECRET_KEY" in keys
    assert len(keys) == 1


def test_load_required_keys_ignores_blank_lines():
    text = "\n  \nAPI_URL\n"
    keys = load_required_keys(text)
    assert keys == {"API_URL"}


def test_load_required_keys_empty_returns_empty_set():
    assert load_required_keys("") == set()


# ---------------------------------------------------------------------------
# check_required
# ---------------------------------------------------------------------------

def test_check_required_all_present():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = check_required(env, {"DB_HOST", "DB_PORT"})
    assert result.ok is True
    assert result.missing == []
    assert set(result.present) == {"DB_HOST", "DB_PORT"}


def test_check_required_some_missing():
    env = {"DB_HOST": "localhost"}
    result = check_required(env, {"DB_HOST", "DB_PORT"})
    assert result.ok is False
    assert len(result.missing) == 1
    assert result.missing[0].key == "DB_PORT"


def test_check_required_all_missing():
    result = check_required({}, {"A", "B"})
    assert result.ok is False
    assert len(result.missing) == 2


def test_check_required_empty_required_set():
    result = check_required({"A": "1"}, set())
    assert result.ok is True


# ---------------------------------------------------------------------------
# check_required_from_text
# ---------------------------------------------------------------------------

def test_check_required_from_text_roundtrip():
    env_text = "DB_HOST=localhost\nDB_PORT=5432\n"
    req_text = "DB_HOST\nDB_PORT\n"
    result = check_required_from_text(env_text, req_text)
    assert result.ok is True


def test_check_required_from_text_missing():
    env_text = "DB_HOST=localhost\n"
    req_text = "DB_HOST\nSECRET_KEY\n"
    result = check_required_from_text(env_text, req_text)
    assert not result.ok
    assert result.missing[0].key == "SECRET_KEY"


# ---------------------------------------------------------------------------
# format_result
# ---------------------------------------------------------------------------

def test_format_result_ok_contains_count():
    result = RequiredCheckResult(present=["A", "B"])
    output = format_result(result)
    assert "2" in output
    assert "present" in output


def test_format_result_missing_shows_key():
    result = RequiredCheckResult(missing=[MissingKeyIssue(key="SECRET")])
    output = format_result(result)
    assert "SECRET" in output
    assert "MISSING" in output
