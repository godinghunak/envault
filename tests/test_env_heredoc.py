"""Tests for envault.env_heredoc."""

import pytest
from envault.env_heredoc import find_heredocs, validate_heredocs, expand_heredocs


SIMPLE = """KEY=value
MULTI=<<EOF
line one
line two
EOF
OTHER=hello
"""

TWO_BLOCKS = """A=<<END
alpha
beta
END
B=<<STOP
gamma
STOP
"""

UNCLOSED = """CERT=<<BLOCK
begin cert
no closing marker here
"""


def test_find_heredocs_returns_pairs():
    pairs = find_heredocs(SIMPLE)
    assert len(pairs) == 1
    assert pairs[0][0] == "MULTI"


def test_find_heredocs_value_content():
    pairs = find_heredocs(SIMPLE)
    assert "line one" in pairs[0][1]
    assert "line two" in pairs[0][1]


def test_find_heredocs_multiple_blocks():
    pairs = find_heredocs(TWO_BLOCKS)
    keys = [k for k, _ in pairs]
    assert "A" in keys
    assert "B" in keys


def test_find_heredocs_empty_text():
    assert find_heredocs("") == []


def test_find_heredocs_no_heredocs():
    text = "FOO=bar\nBAZ=qux\n"
    assert find_heredocs(text) == []


def test_validate_heredocs_clean_returns_empty():
    issues = validate_heredocs(SIMPLE)
    assert issues == []


def test_validate_heredocs_detects_unclosed():
    issues = validate_heredocs(UNCLOSED)
    assert len(issues) == 1
    assert "BLOCK" in str(issues[0])


def test_validate_heredocs_issue_str_contains_line():
    issues = validate_heredocs(UNCLOSED)
    assert "Line" in str(issues[0])


def test_expand_heredocs_returns_dict():
    result = expand_heredocs(SIMPLE)
    assert isinstance(result, dict)
    assert "MULTI" in result


def test_expand_heredocs_value_is_multiline():
    result = expand_heredocs(SIMPLE)
    assert "\n" in result["MULTI"]


def test_expand_heredocs_multiple_blocks():
    result = expand_heredocs(TWO_BLOCKS)
    assert "A" in result
    assert "B" in result
    assert result["A"] == "alpha\nbeta"
    assert result["B"] == "gamma"


def test_expand_heredocs_empty_body():
    text = "EMPTY=<<TAG\nTAG\n"
    result = expand_heredocs(text)
    assert result["EMPTY"] == ""
