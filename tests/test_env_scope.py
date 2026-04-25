"""Tests for envault.env_scope."""
from __future__ import annotations

import pytest

from envault.env_scope import (
    add_scope,
    apply_scope,
    get_scope,
    list_scopes,
    load_scopes,
    remove_scope,
)
from envault.vault import init_vault


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


def test_load_scopes_empty(vault_dir):
    assert load_scopes(vault_dir) == {}


def test_add_scope_stores_keys(vault_dir):
    add_scope(vault_dir, "backend", ["DB_HOST", "DB_PORT"])
    scopes = load_scopes(vault_dir)
    assert "backend" in scopes
    assert set(scopes["backend"]) == {"DB_HOST", "DB_PORT"}


def test_add_scope_deduplicates_keys(vault_dir):
    add_scope(vault_dir, "dup", ["KEY", "KEY", "OTHER"])
    assert load_scopes(vault_dir)["dup"] == ["KEY", "OTHER"]


def test_add_scope_empty_name_raises(vault_dir):
    with pytest.raises(ValueError, match="empty"):
        add_scope(vault_dir, "", ["KEY"])


def test_add_scope_empty_keys_raises(vault_dir):
    with pytest.raises(ValueError, match="at least one key"):
        add_scope(vault_dir, "empty", [])


def test_add_scope_overwrites_existing(vault_dir):
    add_scope(vault_dir, "s", ["A", "B"])
    add_scope(vault_dir, "s", ["C"])
    assert load_scopes(vault_dir)["s"] == ["C"]


def test_remove_scope_deletes_entry(vault_dir):
    add_scope(vault_dir, "to_delete", ["X"])
    remove_scope(vault_dir, "to_delete")
    assert "to_delete" not in load_scopes(vault_dir)


def test_remove_scope_missing_raises(vault_dir):
    with pytest.raises(KeyError):
        remove_scope(vault_dir, "nonexistent")


def test_get_scope_returns_keys(vault_dir):
    add_scope(vault_dir, "frontend", ["API_URL", "APP_NAME"])
    keys = get_scope(vault_dir, "frontend")
    assert keys is not None
    assert set(keys) == {"API_URL", "APP_NAME"}


def test_get_scope_missing_returns_none(vault_dir):
    assert get_scope(vault_dir, "ghost") is None


def test_list_scopes_returns_sorted_names(vault_dir):
    add_scope(vault_dir, "zebra", ["Z"])
    add_scope(vault_dir, "alpha", ["A"])
    assert list_scopes(vault_dir) == ["alpha", "zebra"]


def test_list_scopes_empty(vault_dir):
    assert list_scopes(vault_dir) == []


def test_apply_scope_filters_dict():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
    result = apply_scope(env, ["DB_HOST", "DB_PORT"])
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert "SECRET" not in result


def test_apply_scope_missing_keys_ignored():
    env = {"A": "1"}
    result = apply_scope(env, ["A", "B"])
    assert result == {"A": "1"}


def test_apply_scope_empty_scope():
    env = {"A": "1", "B": "2"}
    result = apply_scope(env, [])
    assert result == {}
