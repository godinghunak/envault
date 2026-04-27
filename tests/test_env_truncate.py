"""Tests for envault.env_truncate."""

import pytest

from envault.env_truncate import (
    TruncationChange,
    truncate_value,
    truncate_dict,
    truncate_env_text,
    DEFAULT_MAX_LENGTH,
    TRUNCATION_SUFFIX,
)


# ---------------------------------------------------------------------------
# truncate_value
# ---------------------------------------------------------------------------

def test_truncate_value_short_string_unchanged():
    assert truncate_value("hello", max_length=20) == "hello"


def test_truncate_value_exact_length_unchanged():
    s = "a" * 10
    assert truncate_value(s, max_length=10) == s


def test_truncate_value_long_string_truncated():
    s = "a" * 200
    result = truncate_value(s, max_length=50)
    assert len(result) == 50
    assert result.endswith(TRUNCATION_SUFFIX)


def test_truncate_value_suffix_preserved():
    s = "x" * 150
    result = truncate_value(s, max_length=20)
    assert result.endswith("...")


def test_truncate_value_default_max_length():
    short = "b" * (DEFAULT_MAX_LENGTH - 1)
    assert truncate_value(short) == short
    long_val = "b" * (DEFAULT_MAX_LENGTH + 50)
    result = truncate_value(long_val)
    assert len(result) == DEFAULT_MAX_LENGTH


# ---------------------------------------------------------------------------
# truncate_dict
# ---------------------------------------------------------------------------

def test_truncate_dict_no_changes_when_short():
    env = {"KEY": "short", "OTHER": "value"}
    result, changes = truncate_dict(env, max_length=50)
    assert result == env
    assert changes == []


def test_truncate_dict_truncates_long_value():
    env = {"KEY": "x" * 200, "SHORT": "ok"}
    result, changes = truncate_dict(env, max_length=50)
    assert len(result["KEY"]) == 50
    assert result["SHORT"] == "ok"
    assert len(changes) == 1
    assert changes[0].key == "KEY"


def test_truncate_dict_change_records_lengths():
    original = "z" * 80
    env = {"K": original}
    _, changes = truncate_dict(env, max_length=30)
    assert changes[0].original_length == 80
    assert changes[0].truncated_length == 30


def test_truncate_dict_keys_filter_respected():
    env = {"A": "x" * 200, "B": "y" * 200}
    result, changes = truncate_dict(env, max_length=50, keys=["A"])
    assert len(result["A"]) == 50
    assert result["B"] == "y" * 200
    assert len(changes) == 1


def test_truncation_change_str():
    tc = TruncationChange("MY_KEY", 200, 50)
    assert "MY_KEY" in str(tc)
    assert "200" in str(tc)
    assert "50" in str(tc)


# ---------------------------------------------------------------------------
# truncate_env_text
# ---------------------------------------------------------------------------

def test_truncate_env_text_preserves_comments():
    text = "# comment\nKEY=value"
    result, _ = truncate_env_text(text, max_length=50)
    assert "# comment" in result


def test_truncate_env_text_preserves_blank_lines():
    text = "KEY=val\n\nOTHER=val2"
    result, _ = truncate_env_text(text, max_length=50)
    assert "\n\n" in result


def test_truncate_env_text_truncates_long_value():
    long_val = "v" * 200
    text = f"KEY={long_val}"
    result, changes = truncate_env_text(text, max_length=50)
    key, _, val = result.partition("=")
    assert len(val) == 50
    assert len(changes) == 1


def test_truncate_env_text_keys_filter():
    text = "A=" + "x" * 200 + "\nB=" + "y" * 200
    result, changes = truncate_env_text(text, max_length=50, keys=["A"])
    lines = result.splitlines()
    a_val = lines[0].split("=", 1)[1]
    b_val = lines[1].split("=", 1)[1]
    assert len(a_val) == 50
    assert len(b_val) == 200
    assert len(changes) == 1
