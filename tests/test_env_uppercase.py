"""Tests for envault.env_uppercase."""

import pytest

from envault.env_uppercase import (
    UppercaseIssue,
    find_non_uppercase,
    uppercase_dict,
    uppercase_env,
)


def test_find_non_uppercase_clean():
    text = "DB_HOST=localhost\nAPI_KEY=abc\n"
    assert find_non_uppercase(text) == []


def test_find_non_uppercase_detects_lowercase_key():
    text = "db_host=localhost\n"
    issues = find_non_uppercase(text)
    assert len(issues) == 1
    assert issues[0].key == "db_host"
    assert issues[0].line_number == 1


def test_find_non_uppercase_detects_mixed_case_key():
    text = "DbHost=localhost\n"
    issues = find_non_uppercase(text)
    assert len(issues) == 1
    assert issues[0].key == "DbHost"


def test_find_non_uppercase_ignores_comments():
    text = "# db_host=localhost\nAPI_KEY=abc\n"
    assert find_non_uppercase(text) == []


def test_find_non_uppercase_ignores_blank_lines():
    text = "\n   \nAPI_KEY=abc\n"
    assert find_non_uppercase(text) == []


def test_find_non_uppercase_correct_line_numbers():
    text = "API_KEY=abc\ndb_pass=secret\nHOST=localhost\n"
    issues = find_non_uppercase(text)
    assert len(issues) == 1
    assert issues[0].line_number == 2


def test_uppercase_env_converts_keys():
    text = "db_host=localhost\napi_key=abc\n"
    result = uppercase_env(text)
    assert "DB_HOST=localhost" in result
    assert "API_KEY=abc" in result


def test_uppercase_env_preserves_already_uppercase():
    text = "DB_HOST=localhost\n"
    result = uppercase_env(text)
    assert result == text


def test_uppercase_env_preserves_comments():
    text = "# my comment\ndb_host=localhost\n"
    result = uppercase_env(text)
    assert "# my comment" in result
    assert "DB_HOST=localhost" in result


def test_uppercase_env_preserves_trailing_newline():
    text = "db_host=localhost\n"
    result = uppercase_env(text)
    assert result.endswith("\n")


def test_uppercase_env_no_trailing_newline():
    text = "db_host=localhost"
    result = uppercase_env(text)
    assert not result.endswith("\n")
    assert "DB_HOST=localhost" in result


def test_uppercase_dict_converts_keys():
    d = {"db_host": "localhost", "Api_Key": "abc"}
    result = uppercase_dict(d)
    assert result == {"DB_HOST": "localhost", "API_KEY": "abc"}


def test_uppercase_dict_empty():
    assert uppercase_dict({}) == {}


def test_uppercase_issue_str():
    issue = UppercaseIssue(key="db_host", line_number=3)
    assert "db_host" in str(issue)
    assert "3" in str(issue)
