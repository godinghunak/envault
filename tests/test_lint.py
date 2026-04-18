"""Tests for envault.lint."""
import pytest
from envault.lint import lint_env, LintIssue


def test_no_issues_clean_file():
    content = "DB_HOST=localhost\nDB_PORT=5432\n"
    assert lint_env(content) == []


def test_ignores_comments_and_blanks():
    content = "# comment\n\nAPI_KEY=secret\n"
    assert lint_env(content) == []


def test_missing_equals():
    issues = lint_env("BADLINE\n")
    assert any(i.code == "E001" for i in issues)


def test_empty_key():
    issues = lint_env("=value\n")
    assert any(i.code == "E002" for i in issues)


def test_key_with_spaces():
    issues = lint_env("MY KEY=value\n")
    assert any(i.code == "E003" for i in issues)


def test_lowercase_key_warning():
    issues = lint_env("my_key=value\n")
    codes = [i.code for i in issues]
    assert "W001" in codes


def test_duplicate_key_warning():
    content = "API_KEY=abc\nAPI_KEY=xyz\n"
    issues = lint_env(content)
    assert any(i.code == "W002" for i in issues)


def test_empty_value_warning():
    issues = lint_env("API_KEY=\n")
    assert any(i.code == "W004" for i in issues)


def test_multiple_issues():
    content = "bad line\nmy_key=\nAPI=ok\n"
    issues = lint_env(content)
    codes = {i.code for i in issues}
    assert "E001" in codes
    assert "W001" in codes
    assert "W004" in codes


def test_issue_str():
    issue = LintIssue(3, "W001", "Key not uppercase: 'foo'")
    assert "Line 3" in str(issue)
    assert "W001" in str(issue)
