"""Tests for envault.env_filter."""
import pytest
from envault.env_filter import filter_env, filter_by_prefix, format_filtered


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_SECRET": "abc",
    "APP_DEBUG": "true",
    "LOG_LEVEL": "info",
}


def test_filter_env_glob_all():
    assert filter_env(SAMPLE, "*") == SAMPLE


def test_filter_env_glob_prefix_pattern():
    result = filter_env(SAMPLE, "DB_*")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_env_no_match():
    result = filter_env(SAMPLE, "MISSING_*")
    assert result == {}


def test_filter_env_exact_key():
    result = filter_env(SAMPLE, "LOG_LEVEL")
    assert result == {"LOG_LEVEL": "info"}


def test_filter_by_prefix_db():
    result = filter_by_prefix(SAMPLE, "DB_")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_prefix_app():
    result = filter_by_prefix(SAMPLE, "APP_")
    assert set(result.keys()) == {"APP_SECRET", "APP_DEBUG"}


def test_filter_by_prefix_no_match():
    result = filter_by_prefix(SAMPLE, "NOPE_")
    assert result == {}


def test_format_filtered_sorted():
    env = {"B": "2", "A": "1"}
    out = format_filtered(env)
    assert out == "A=1\nB=2"


def test_format_filtered_empty():
    assert format_filtered({}) == ""
