"""Tests for envault.diff module."""
import pytest
from envault.diff import parse_env, diff_envs, format_diff


def test_parse_env_basic():
    content = "FOO=bar\nBAZ=qux\n"
    result = parse_env(content)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_ignores_comments():
    content = "# comment\nFOO=bar\n"
    result = parse_env(content)
    assert "FOO" in result
    assert len(result) == 1


def test_parse_env_ignores_blank_lines():
    content = "\nFOO=bar\n\n"
    assert parse_env(content) == {"FOO": "bar"}


def test_diff_added():
    old = {"A": "1"}
    new = {"A": "1", "B": "2"}
    diff = diff_envs(old, new)
    statuses = {k: s for s, k, *_ in diff}
    assert statuses["B"] == "added"
    assert statuses["A"] == "unchanged"


def test_diff_removed():
    old = {"A": "1", "B": "2"}
    new = {"A": "1"}
    diff = diff_envs(old, new)
    statuses = {k: s for s, k, *_ in diff}
    assert statuses["B"] == "removed"


def test_diff_changed():
    old = {"A": "1"}
    new = {"A": "2"}
    diff = diff_envs(old, new)
    assert diff[0][0] == "changed"


def test_diff_unchanged():
    env = {"A": "1"}
    diff = diff_envs(env, env)
    assert diff[0][0] == "unchanged"


def test_format_diff_no_changes():
    env = {"A": "1"}
    diff = diff_envs(env, env)
    assert format_diff(diff) == "(no changes)"


def test_format_diff_shows_added():
    diff = [("added", "B", None, "2")]
    out = format_diff(diff)
    assert out.startswith("+")
    assert "B" in out


def test_format_diff_show_values():
    diff = [("changed", "A", "1", "2")]
    out = format_diff(diff, show_values=True)
    assert "1" in out and "2" in out


def test_format_diff_hides_values_by_default():
    diff = [("changed", "SECRET", "hunter2", "newpass")]
    out = format_diff(diff, show_values=False)
    assert "hunter2" not in out
    assert "newpass" not in out
