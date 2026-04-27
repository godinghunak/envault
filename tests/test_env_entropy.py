"""Tests for envault.env_entropy — entropy analysis of .env values."""

import pytest
from envault.env_entropy import (
    _shannon_entropy,
    _is_sensitive_key,
    analyze_value,
    analyze_dict,
    weak_results,
    format_entropy_report,
)


# ---------------------------------------------------------------------------
# _shannon_entropy
# ---------------------------------------------------------------------------

def test_entropy_empty_string_is_zero():
    assert _shannon_entropy("") == 0.0


def test_entropy_single_char_is_zero():
    assert _shannon_entropy("aaaa") == 0.0


def test_entropy_two_equal_symbols():
    result = _shannon_entropy("abababab")
    assert abs(result - 1.0) < 1e-9


def test_entropy_high_for_random_string():
    value = "aB3$xYz!9qW#mNpL"
    assert _shannon_entropy(value) > 3.5


# ---------------------------------------------------------------------------
# _is_sensitive_key
# ---------------------------------------------------------------------------

def test_is_sensitive_password():
    assert _is_sensitive_key("DB_PASSWORD") is True


def test_is_sensitive_api_key():
    assert _is_sensitive_key("STRIPE_API_KEY") is True


def test_is_sensitive_token():
    assert _is_sensitive_key("AUTH_TOKEN") is True


def test_is_sensitive_normal_key():
    assert _is_sensitive_key("APP_HOST") is False


# ---------------------------------------------------------------------------
# analyze_value
# ---------------------------------------------------------------------------

def test_analyze_value_strong_secret_is_ok():
    result = analyze_value("API_KEY", "aB3$xYz!9qW#mNpL")
    assert result.is_weak is False


def test_analyze_value_short_secret_is_weak():
    result = analyze_value("API_SECRET", "abc")
    assert result.is_weak is True
    assert "short" in result.reason


def test_analyze_value_low_entropy_secret_is_weak():
    result = analyze_value("DB_PASSWORD", "aaaaaaaa")
    assert result.is_weak is True
    assert "entropy" in result.reason


def test_analyze_value_non_sensitive_key_never_weak():
    result = analyze_value("APP_HOST", "a")
    assert result.is_weak is False


def test_analyze_value_empty_sensitive_key_is_weak():
    result = analyze_value("AUTH_TOKEN", "")
    assert result.is_weak is True


def test_analyze_value_entropy_field_populated():
    result = analyze_value("SOME_KEY", "hello")
    assert result.entropy > 0.0


# ---------------------------------------------------------------------------
# analyze_dict / weak_results / format_entropy_report
# ---------------------------------------------------------------------------

def test_analyze_dict_returns_one_result_per_key():
    env = {"API_KEY": "strongXY99!!", "APP_PORT": "8080"}
    results = analyze_dict(env)
    assert len(results) == 2


def test_weak_results_filters_correctly():
    env = {"DB_PASSWORD": "aaa", "APP_HOST": "localhost"}
    results = analyze_dict(env)
    weak = weak_results(results)
    assert len(weak) == 1
    assert weak[0].key == "DB_PASSWORD"


def test_format_entropy_report_no_issues():
    env = {"API_TOKEN": "aB3$xYz!9qW#mNpL"}
    results = analyze_dict(env)
    output = format_entropy_report(results, only_weak=True)
    assert "No issues" in output


def test_format_entropy_report_shows_weak_key():
    env = {"DB_PASSWORD": "aaaa", "APP_HOST": "localhost"}
    results = analyze_dict(env)
    output = format_entropy_report(results, only_weak=True)
    assert "DB_PASSWORD" in output
    assert "WEAK" in output
