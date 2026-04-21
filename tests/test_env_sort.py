"""Tests for envault.env_sort."""

import pytest
from envault.env_sort import sort_env, sort_dict, parse_env_lines


SIMPLE_ENV = """ZEBRA=1
APPLE=2
MANGO=3
"""

ENV_WITH_COMMENTS = """# Top comment

ZEBRA=1
# Mango note
MANGO=3
APPLE=2
"""


def test_sort_env_alphabetical():
    result = sort_env(SIMPLE_ENV)
    keys = [l.split("=")[0] for l in result.splitlines() if "=" in l]
    assert keys == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_env_reverse():
    result = sort_env(SIMPLE_ENV, reverse=True)
    keys = [l.split("=")[0] for l in result.splitlines() if "=" in l]
    assert keys == ["ZEBRA", "MANGO", "APPLE"]


def test_sort_env_preserves_values():
    result = sort_env(SIMPLE_ENV)
    assert "APPLE=2" in result
    assert "MANGO=3" in result
    assert "ZEBRA=1" in result


def test_sort_env_preserves_top_comment():
    result = sort_env(ENV_WITH_COMMENTS)
    assert result.startswith("# Top comment")


def test_sort_env_comment_attached_to_key():
    result = sort_env(ENV_WITH_COMMENTS)
    lines = result.splitlines()
    mango_comment_idx = next(i for i, l in enumerate(lines) if l.strip() == "# Mango note")
    mango_key_idx = next(i for i, l in enumerate(lines) if l.startswith("MANGO="))
    assert mango_key_idx == mango_comment_idx + 1


def test_sort_env_custom_order():
    result = sort_env(SIMPLE_ENV, custom_order=["MANGO", "ZEBRA", "APPLE"])
    keys = [l.split("=")[0] for l in result.splitlines() if "=" in l]
    assert keys == ["MANGO", "ZEBRA", "APPLE"]


def test_sort_env_custom_order_partial():
    """Keys not in custom_order should appear after, sorted alphabetically."""
    env = "DELTA=4\nALPHA=1\nBETA=2\nGAMMA=3\n"
    result = sort_env(env, custom_order=["GAMMA"])
    keys = [l.split("=")[0] for l in result.splitlines() if "=" in l]
    assert keys[0] == "GAMMA"
    assert keys[1:] == sorted(["ALPHA", "BETA", "DELTA"])


def test_sort_env_empty_string():
    assert sort_env("") == ""


def test_sort_env_only_comments():
    text = "# just a comment\n# another"
    result = sort_env(text)
    assert "# just a comment" in result
    assert "# another" in result


def test_sort_dict_alphabetical():
    d = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}
    result = sort_dict(d)
    assert list(result.keys()) == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_dict_reverse():
    d = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}
    result = sort_dict(d, reverse=True)
    assert list(result.keys()) == ["ZEBRA", "MANGO", "APPLE"]


def test_parse_env_lines_identifies_keys():
    lines = parse_env_lines("A=1\nB=2\n")
    keys = [k for k, _ in lines if k]
    assert keys == ["A", "B"]


def test_parse_env_lines_blank_has_empty_key():
    lines = parse_env_lines("\n")
    assert lines[0][0] == ""
