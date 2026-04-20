"""Tests for envault/env_split.py"""

import pytest
from envault.env_split import (
    split_by_prefix,
    split_by_keys,
    split_env_text,
    format_split_part,
    SplitResult,
)


ENV_TEXT = """DB_HOST=localhost
DB_PORT=5432
AWS_KEY=abc123
AWS_SECRET=xyz
APP_NAME=myapp
DEBUG=true
"""


def test_split_by_prefix_groups_correctly():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "AWS_KEY": "abc"}
    result = split_by_prefix(env)
    assert "db" in result.names()
    assert "aws" in result.names()
    assert result.get("db")["DB_HOST"] == "localhost"
    assert result.get("db")["DB_PORT"] == "5432"
    assert result.get("aws")["AWS_KEY"] == "abc"


def test_split_by_prefix_no_sep_goes_to_other():
    env = {"DEBUG": "true", "DB_HOST": "localhost"}
    result = split_by_prefix(env)
    assert "other" in result.names()
    assert result.get("other")["DEBUG"] == "true"


def test_split_by_prefix_empty_env():
    result = split_by_prefix({})
    assert result.names() == []


def test_split_by_keys_assigns_correctly():
    env = {"DB_HOST": "localhost", "AWS_KEY": "abc", "APP_NAME": "myapp"}
    groups = {"database": ["DB_HOST"], "cloud": ["AWS_KEY"]}
    result = split_by_keys(env, groups)
    assert result.get("database")["DB_HOST"] == "localhost"
    assert result.get("cloud")["AWS_KEY"] == "abc"
    assert result.get("other")["APP_NAME"] == "myapp"


def test_split_by_keys_missing_key_ignored():
    env = {"DB_HOST": "localhost"}
    groups = {"database": ["DB_HOST", "DB_PORT"]}
    result = split_by_keys(env, groups)
    assert "DB_PORT" not in result.get("database")


def test_split_by_keys_no_leftover():
    env = {"DB_HOST": "localhost"}
    groups = {"database": ["DB_HOST"]}
    result = split_by_keys(env, groups)
    assert "other" not in result.parts


def test_split_env_text_parses_and_splits():
    result = split_env_text(ENV_TEXT)
    assert "db" in result.names()
    assert "aws" in result.names()
    assert "app" in result.names()


def test_format_split_part_produces_env_lines():
    data = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    text = format_split_part(data)
    assert "DB_HOST=localhost" in text
    assert "DB_PORT=5432" in text


def test_format_split_part_empty():
    text = format_split_part({})
    assert text == ""


def test_split_result_names_sorted():
    r = SplitResult()
    r.add("z_group", {"Z": "1"})
    r.add("a_group", {"A": "2"})
    assert r.names() == ["a_group", "z_group"]
