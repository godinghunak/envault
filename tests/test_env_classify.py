"""Tests for envault.env_classify."""

import pytest
from envault.env_classify import (
    classify_key,
    classify_env,
    format_classify_result,
    ClassifyResult,
    ClassifiedKey,
)


# ---------------------------------------------------------------------------
# classify_key
# ---------------------------------------------------------------------------

def test_classify_key_database():
    assert classify_key("DB_HOST") == "database"


def test_classify_key_database_postgres():
    assert classify_key("POSTGRES_PASSWORD") == "database"


def test_classify_key_auth_token():
    assert classify_key("JWT_TOKEN") == "auth"


def test_classify_key_auth_secret():
    assert classify_key("APP_SECRET_KEY") == "auth"


def test_classify_key_api_url():
    assert classify_key("API_BASE_URL") == "api"


def test_classify_key_api_host():
    assert classify_key("SERVICE_HOST") == "api"


def test_classify_key_cloud_aws():
    assert classify_key("AWS_ACCESS_KEY_ID") == "cloud"


def test_classify_key_email_smtp():
    assert classify_key("SMTP_HOST") == "email"


def test_classify_key_logging_sentry():
    assert classify_key("SENTRY_DSN") == "logging"


def test_classify_key_feature_flag():
    assert classify_key("FEATURE_DARK_MODE") == "feature"


def test_classify_key_other():
    assert classify_key("APP_NAME") == "other"


def test_classify_key_case_insensitive():
    assert classify_key("db_host") == "database"


# ---------------------------------------------------------------------------
# classify_env
# ---------------------------------------------------------------------------

def test_classify_env_empty():
    result = classify_env({})
    assert result.total() == 0
    assert result.all_categories() == []


def test_classify_env_groups_correctly():
    env = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "SECRET_KEY": "abc123",
        "APP_NAME": "myapp",
    }
    result = classify_env(env)
    assert len(result.get("database")) == 2
    assert len(result.get("auth")) == 1
    assert len(result.get("other")) == 1


def test_classify_env_total_equals_input_size():
    env = {"A": "1", "B": "2", "C": "3"}
    result = classify_env(env)
    assert result.total() == 3


def test_classify_env_classified_key_attributes():
    env = {"AWS_REGION": "us-east-1"}
    result = classify_env(env)
    items = result.get("cloud")
    assert len(items) == 1
    assert items[0].key == "AWS_REGION"
    assert items[0].value == "us-east-1"
    assert items[0].category == "cloud"


# ---------------------------------------------------------------------------
# format_classify_result
# ---------------------------------------------------------------------------

def test_format_classify_result_empty():
    result = ClassifyResult()
    output = format_classify_result(result)
    assert output == "No keys to classify."


def test_format_classify_result_contains_category_header():
    env = {"DB_HOST": "localhost"}
    result = classify_env(env)
    output = format_classify_result(result)
    assert "[database]" in output
    assert "DB_HOST" in output


def test_format_classify_result_shows_key_count():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = classify_env(env)
    output = format_classify_result(result)
    assert "2 key(s)" in output
