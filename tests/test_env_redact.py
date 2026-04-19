"""Tests for envault.env_redact."""

import pytest
from envault.env_redact import is_sensitive, redact_line, redact_env, redact_dict, REDACT_PLACEHOLDER


def test_is_sensitive_password():
    assert is_sensitive("PASSWORD") is True

def test_is_sensitive_api_key():
    assert is_sensitive("STRIPE_API_KEY") is True

def test_is_sensitive_token():
    assert is_sensitive("AUTH_TOKEN") is True

def test_is_sensitive_normal_key():
    assert is_sensitive("APP_ENV") is False
    assert is_sensitive("PORT") is False

def test_redact_line_sensitive():
    result = redact_line("DB_PASSWORD=supersecret\n")
    assert REDACT_PLACEHOLDER in result
    assert "supersecret" not in result

def test_redact_line_non_sensitive():
    line = "APP_ENV=production\n"
    assert redact_line(line) == line

def test_redact_line_comment_unchanged():
    line = "# DB_PASSWORD=secret\n"
    assert redact_line(line) == line

def test_redact_line_blank_unchanged():
    assert redact_line("\n") == "\n"

def test_redact_env_mixed():
    content = "APP_ENV=production\nDB_PASSWORD=secret\nPORT=5432\n"
    result = redact_env(content)
    assert "production" in result
    assert "secret" not in result
    assert REDACT_PLACEHOLDER in result
    assert "5432" in result

def test_redact_dict_sensitive_keys():
    env = {"APP_ENV": "prod", "SECRET_KEY": "abc123", "PORT": "8080"}
    result = redact_dict(env)
    assert result["APP_ENV"] == "prod"
    assert result["SECRET_KEY"] == REDACT_PLACEHOLDER
    assert result["PORT"] == "8080"

def test_redact_dict_empty_value_not_redacted():
    env = {"API_KEY": ""}
    result = redact_dict(env)
    assert result["API_KEY"] == ""
