"""Tests for envault.env_prefix."""

import pytest

from envault.env_prefix import (
    add_prefix,
    strip_prefix,
    replace_prefix,
    diff_prefix_changes,
    list_prefixes,
    PrefixChange,
)


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_DEBUG": "true",
    "SECRET_KEY": "abc123",
}


def test_add_prefix_prepends_to_all_keys():
    result = add_prefix({"HOST": "localhost", "PORT": "5432"}, "DB_")
    assert "DB_HOST" in result
    assert "DB_PORT" in result
    assert result["DB_HOST"] == "localhost"


def test_add_prefix_normalises_to_uppercase():
    result = add_prefix({"HOST": "x"}, "app_")
    assert "APP_HOST" in result


def test_strip_prefix_removes_matching():
    result = strip_prefix({"DB_HOST": "localhost", "DB_PORT": "5432"}, "DB_")
    assert "HOST" in result
    assert "PORT" in result
    assert "DB_HOST" not in result


def test_strip_prefix_leaves_non_matching_unchanged():
    result = strip_prefix(SAMPLE, "DB_")
    assert "APP_DEBUG" in result
    assert "SECRET_KEY" in result
    assert "HOST" in result
    assert "PORT" in result


def test_strip_prefix_empty_env():
    assert strip_prefix({}, "ANYTHING_") == {}


def test_replace_prefix_swaps_matching_keys():
    result = replace_prefix({"OLD_HOST": "h", "OLD_PORT": "p"}, "OLD_", "NEW_")
    assert "NEW_HOST" in result
    assert "NEW_PORT" in result
    assert "OLD_HOST" not in result


def test_replace_prefix_leaves_non_matching():
    result = replace_prefix(SAMPLE, "DB_", "DATABASE_")
    assert "DATABASE_HOST" in result
    assert "DATABASE_PORT" in result
    assert "APP_DEBUG" in result


def test_replace_prefix_no_match_returns_original():
    result = replace_prefix({"FOO": "bar"}, "MISSING_", "NEW_")
    assert result == {"FOO": "bar"}


def test_diff_prefix_changes_detects_renames():
    original = {"OLD_HOST": "localhost"}
    updated = {"NEW_HOST": "localhost"}
    changes = diff_prefix_changes(original, updated)
    assert len(changes) == 1
    assert changes[0].old_key == "OLD_HOST"
    assert changes[0].new_key == "NEW_HOST"


def test_diff_prefix_changes_no_change_returns_empty():
    env = {"HOST": "localhost"}
    changes = diff_prefix_changes(env, env.copy())
    assert changes == []


def test_list_prefixes_extracts_unique_prefixes():
    env = {"DB_HOST": "h", "DB_PORT": "p", "APP_DEBUG": "true", "NOPREFIX": "x"}
    prefixes = list_prefixes(env)
    assert "DB" in prefixes
    assert "APP" in prefixes
    assert "NOPREFIX" not in prefixes


def test_list_prefixes_empty_env():
    assert list_prefixes({}) == []


def test_list_prefixes_custom_separator():
    env = {"NS.KEY": "val", "NS.OTHER": "v2", "BARE": "x"}
    prefixes = list_prefixes(env, separator=".")
    assert prefixes == ["NS"]


def test_prefix_change_str():
    c = PrefixChange(key="NEW_HOST", old_key="OLD_HOST", new_key="NEW_HOST", value="localhost")
    assert "OLD_HOST" in str(c)
    assert "NEW_HOST" in str(c)
