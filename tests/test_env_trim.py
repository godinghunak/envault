import pytest
from envault.env_trim import trim_value, trim_env, find_untrimmed, trim_env_text


def test_trim_value_strips_spaces():
    assert trim_value("  hello  ") == "hello"


def test_trim_value_strips_tabs():
    assert trim_value("\tvalue\t") == "value"


def test_trim_value_clean_unchanged():
    assert trim_value("clean") == "clean"


def test_trim_value_empty_string():
    assert trim_value("") == ""


def test_trim_env_trims_all_values():
    env = {"A": "  foo  ", "B": "bar", "C": "  baz"}
    result = trim_env(env)
    assert result == {"A": "foo", "B": "bar", "C": "baz"}


def test_trim_env_empty_dict():
    assert trim_env({}) == {}


def test_find_untrimmed_detects_padded():
    env = {"A": "  hello  ", "B": "clean"}
    issues = find_untrimmed(env)
    assert len(issues) == 1
    key, original, trimmed = issues[0]
    assert key == "A"
    assert original == "  hello  "
    assert trimmed == "hello"


def test_find_untrimmed_empty_returns_empty():
    assert find_untrimmed({"A": "ok", "B": "fine"}) == []


def test_trim_env_text_preserves_comments():
    text = "# comment\nA=  value  \nB=clean"
    result = trim_env_text(text)
    assert "# comment" in result
    assert "A=value" in result
    assert "B=clean" in result


def test_trim_env_text_preserves_blank_lines():
    text = "A=hello\n\nB=world"
    result = trim_env_text(text)
    lines = result.splitlines()
    assert "" in lines


def test_trim_env_text_trims_leading_spaces():
    text = "KEY=   spaced"
    result = trim_env_text(text)
    assert result == "KEY=spaced"


def test_trim_env_text_trims_trailing_spaces():
    text = "KEY=value   "
    result = trim_env_text(text)
    assert result == "KEY=value"


def test_trim_env_text_no_equals_line_unchanged():
    text = "NOEQUALS"
    result = trim_env_text(text)
    assert result == "NOEQUALS"
