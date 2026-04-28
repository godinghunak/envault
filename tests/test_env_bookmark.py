"""Unit tests for envault.env_bookmark."""

from __future__ import annotations

import pytest

from envault.env_bookmark import (
    add_bookmark,
    list_bookmarks,
    load_bookmarks,
    remove_bookmark,
    resolve_bookmark,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_load_bookmarks_empty(vault_dir):
    assert load_bookmarks(vault_dir) == {}


def test_add_bookmark_stores_entry(vault_dir):
    add_bookmark(vault_dir, "stable", 3)
    assert load_bookmarks(vault_dir)["stable"] == 3


def test_add_bookmark_overwrites(vault_dir):
    add_bookmark(vault_dir, "stable", 3)
    add_bookmark(vault_dir, "stable", 7)
    assert load_bookmarks(vault_dir)["stable"] == 7


def test_add_bookmark_empty_name_raises(vault_dir):
    with pytest.raises(ValueError, match="empty"):
        add_bookmark(vault_dir, "", 1)


def test_add_bookmark_invalid_version_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid version"):
        add_bookmark(vault_dir, "bad", 0)


def test_remove_bookmark_deletes_entry(vault_dir):
    add_bookmark(vault_dir, "old", 2)
    remove_bookmark(vault_dir, "old")
    assert "old" not in load_bookmarks(vault_dir)


def test_remove_bookmark_missing_raises(vault_dir):
    with pytest.raises(KeyError, match="not found"):
        remove_bookmark(vault_dir, "nonexistent")


def test_resolve_bookmark_returns_version(vault_dir):
    add_bookmark(vault_dir, "prod", 5)
    assert resolve_bookmark(vault_dir, "prod") == 5


def test_resolve_bookmark_missing_returns_none(vault_dir):
    assert resolve_bookmark(vault_dir, "ghost") is None


def test_list_bookmarks_sorted(vault_dir):
    add_bookmark(vault_dir, "zeta", 1)
    add_bookmark(vault_dir, "alpha", 2)
    names = [name for name, _ in list_bookmarks(vault_dir)]
    assert names == sorted(names)


def test_list_bookmarks_empty(vault_dir):
    assert list_bookmarks(vault_dir) == []


def test_multiple_bookmarks(vault_dir):
    add_bookmark(vault_dir, "dev", 1)
    add_bookmark(vault_dir, "staging", 4)
    add_bookmark(vault_dir, "prod", 9)
    entries = dict(list_bookmarks(vault_dir))
    assert entries["dev"] == 1
    assert entries["staging"] == 4
    assert entries["prod"] == 9
