import pytest
from envault.env_normalize import (
    normalize_value,
    normalize_env,
    NormalizeIssue,
    _strip_inline_comment,
    _quote_if_needed,
)


# --- _strip_inline_comment ---

def test_strip_inline_comment_removes_trailing_comment():
    assert _strip_inline_comment("hello # world") == "hello"


def test_strip_inline_comment_no_comment_unchanged():
    assert _strip_inline_comment("hello") == "hello"


def test_strip_inline_comment_ignores_quoted_value():
    assert _strip_inline_comment('"hello # world"') == '"hello # world"'


def test_strip_inline_comment_hash_without_space_unchanged():
    assert _strip_inline_comment("abc#def") == "abc#def"


# --- _quote_if_needed ---

def test_quote_if_needed_spaces_quoted():
    assert _quote_if_needed("hello world") == '"hello world"'


def test_quote_if_needed_no_spaces_unchanged():
    assert _quote_if_needed("helloworld") == "helloworld"


def test_quote_if_needed_already_quoted_unchanged():
    assert _quote_if_needed('"hello world"') == '"hello world"'


def test_quote_if_needed_single_quoted_unchanged():
    assert _quote_if_needed("'hello world'") == "'hello world'"


def test_quote_if_needed_escapes_inner_double_quotes():
    result = _quote_if_needed('say "hi" now')
    assert result == '"say \\"hi\\" now"'


# --- normalize_value ---

def test_normalize_value_strips_then_quotes():
    result = normalize_value("hello world # comment")
    assert result == '"hello world"'


def test_normalize_value_clean_value_unchanged():
    assert normalize_value("cleanvalue") == "cleanvalue"


# --- normalize_env ---

def test_normalize_env_no_changes_returns_empty_issues():
    text = "KEY=value\nOTHER=123"
    out, issues = normalize_env(text)
    assert issues == []
    assert "KEY=value" in out


def test_normalize_env_strips_inline_comment():
    text = "KEY=value # this is a comment"
    out, issues = normalize_env(text)
    assert "KEY=value" in out
    assert len(issues) == 1
    assert issues[0].key == "KEY"


def test_normalize_env_quotes_spaced_value():
    text = "GREETING=hello world"
    out, issues = normalize_env(text)
    assert 'GREETING="hello world"' in out
    assert len(issues) == 1


def test_normalize_env_preserves_comments_and_blanks():
    text = "# comment\n\nKEY=val"
    out, issues = normalize_env(text)
    assert "# comment" in out
    assert issues == []


def test_normalize_env_issue_contains_line_number():
    text = "A=1\nB=hello world\nC=3"
    _, issues = normalize_env(text)
    assert issues[0].line_number == 2


def test_normalize_env_issue_str_contains_key():
    text = "MYKEY=spaced value"
    _, issues = normalize_env(text)
    assert "MYKEY" in str(issues[0])


def test_normalize_env_multiple_issues():
    text = "A=foo bar\nB=baz # comment\nC=ok"
    _, issues = normalize_env(text)
    assert len(issues) == 2
