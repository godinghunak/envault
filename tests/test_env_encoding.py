"""Tests for envault.env_encoding module."""

import pytest
from envault.env_encoding import (
    EncodingIssue,
    find_encoding_issues,
    normalize_encoding,
    encoding_issues_from_text,
    format_encoding_report,
)


def test_find_encoding_issues_clean():
    env = {"HOST": "localhost", "PORT": "5432"}
    assert find_encoding_issues(env) == []


def test_find_encoding_issues_non_ascii():
    env = {"GREETING": "héllo"}
    issues = find_encoding_issues(env)
    assert len(issues) == 1
    assert issues[0].key == "GREETING"
    assert "non-ASCII" in issues[0].reason


def test_find_encoding_issues_control_character():
    env = {"BAD": "val\x01ue"}
    issues = find_encoding_issues(env)
    assert len(issues) == 1
    assert "control character" in issues[0].reason


def test_find_encoding_issues_tab_is_allowed():
    # Tab (0x09) should NOT be flagged as a control character
    env = {"INDENTED": "val\tue"}
    issues = find_encoding_issues(env)
    assert issues == []


def test_find_encoding_issues_multiple():
    env = {
        "A": "ok",
        "B": "caf\u00e9",
        "C": "bad\x00val",
    }
    issues = find_encoding_issues(env)
    assert len(issues) == 2
    keys = {i.key for i in issues}
    assert keys == {"B", "C"}


def test_normalize_encoding_strips_whitespace():
    env = {"KEY": "  value  "}
    result = normalize_encoding(env)
    assert result["KEY"] == "value"


def test_normalize_encoding_nfc():
    # Compose e + combining acute -> single é
    decomposed = "e\u0301"  # NFC would be \u00e9
    env = {"KEY": decomposed}
    result = normalize_encoding(env)
    assert result["KEY"] == "\u00e9"


def test_normalize_encoding_preserves_keys():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = normalize_encoding(env)
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_encoding_issues_from_text_no_issues():
    text = "HOST=localhost\nPORT=5432\n"
    issues = encoding_issues_from_text(text)
    assert issues == []


def test_encoding_issues_from_text_skips_comments_and_blanks():
    text = "# comment\n\nHOST=ok\n"
    issues = encoding_issues_from_text(text)
    assert issues == []


def test_encoding_issues_from_text_detects_non_ascii():
    text = "NAME=Jos\u00e9\n"
    issues = encoding_issues_from_text(text)
    assert len(issues) == 1
    assert issues[0].key == "NAME"


def test_format_encoding_report_no_issues():
    report = format_encoding_report([])
    assert "No encoding issues" in report


def test_format_encoding_report_with_issues():
    issues = [EncodingIssue("KEY", "val\u00e9", "contains non-ASCII characters")]
    report = format_encoding_report(issues)
    assert "1 encoding issue" in report
    assert "KEY" in report


def test_encoding_issue_str():
    issue = EncodingIssue("MY_KEY", "bad\x01", "contains control character")
    s = str(issue)
    assert "MY_KEY" in s
    assert "control character" in s
