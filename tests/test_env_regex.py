"""Tests for envault.env_regex."""
import pytest
from envault.env_regex import (
    match_keys,
    match_values,
    validate_values,
    format_regex_result,
    RegexResult,
)

SAMPLE: dict[str, str] = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "API_KEY": "abc123",
    "APP_DEBUG": "true",
    "SECRET_TOKEN": "s3cr3t!",
}


def test_match_keys_prefix():
    result = match_keys(SAMPLE, r"^DB_")
    keys = {m.key for m in result.matches}
    assert keys == {"DB_HOST", "DB_PORT"}


def test_match_keys_no_match():
    result = match_keys(SAMPLE, r"^NONEXISTENT")
    assert len(result.matches) == 0
    assert result.ok


def test_match_keys_invalid_pattern():
    result = match_keys(SAMPLE, r"[invalid")
    assert not result.ok
    assert len(result.errors) == 1
    assert "Invalid pattern" in result.errors[0]


def test_match_values_numeric():
    result = match_values(SAMPLE, r"^\d+$")
    keys = {m.key for m in result.matches}
    assert keys == {"DB_PORT"}


def test_match_values_contains_secret():
    result = match_values(SAMPLE, r"s3cr3t")
    assert len(result.matches) == 1
    assert result.matches[0].key == "SECRET_TOKEN"


def test_match_values_invalid_pattern():
    result = match_values(SAMPLE, r"(unclosed")
    assert not result.ok


def test_validate_values_all_pass():
    rules = {"DB_PORT": r"\d+", "APP_DEBUG": r"true|false"}
    result = validate_values(SAMPLE, rules)
    assert result.ok
    assert len(result.matches) == 2


def test_validate_values_one_fails():
    rules = {"DB_PORT": r"\d+", "API_KEY": r"^[A-Z]+$"}  # API_KEY won't match
    result = validate_values(SAMPLE, rules)
    assert not result.ok
    assert any("API_KEY" in e for e in result.errors)


def test_validate_values_missing_key_skipped():
    rules = {"MISSING_KEY": r".*"}
    result = validate_values(SAMPLE, rules)
    assert result.ok
    assert len(result.matches) == 0


def test_validate_values_invalid_rule_pattern():
    rules = {"DB_PORT": r"[bad"}
    result = validate_values(SAMPLE, rules)
    assert not result.ok
    assert "Invalid rule pattern" in result.errors[0]


def test_format_regex_result_with_matches():
    result = match_keys(SAMPLE, r"^DB_")
    output = format_regex_result(result)
    assert "Matches" in output
    assert "DB_HOST" in output


def test_format_regex_result_no_matches():
    result = match_keys(SAMPLE, r"^ZZZNOPE")
    output = format_regex_result(result)
    assert "No matches found" in output


def test_format_regex_result_with_errors():
    result = match_keys(SAMPLE, r"[bad")
    output = format_regex_result(result)
    assert "Errors" in output


def test_regex_match_str():
    result = match_keys(SAMPLE, r"^API")
    assert len(result.matches) == 1
    s = str(result.matches[0])
    assert "API_KEY" in s
    assert "abc123" in s
