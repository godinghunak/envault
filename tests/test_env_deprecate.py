"""Tests for envault/env_deprecate.py"""

from __future__ import annotations

import pytest

from envault.env_deprecate import (
    check_env_for_deprecated,
    deprecate_key,
    get_deprecation,
    list_deprecated,
    load_deprecations,
    undeprecate_key,
)
from envault.vault import init_vault


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


def test_load_deprecations_empty(vault_dir):
    assert load_deprecations(vault_dir) == {}


def test_deprecate_key_stores_entry(vault_dir):
    deprecate_key(vault_dir, "OLD_KEY", reason="Use NEW_KEY", replacement="NEW_KEY")
    data = load_deprecations(vault_dir)
    assert "OLD_KEY" in data
    assert data["OLD_KEY"]["reason"] == "Use NEW_KEY"
    assert data["OLD_KEY"]["replacement"] == "NEW_KEY"


def test_deprecate_key_no_replacement(vault_dir):
    deprecate_key(vault_dir, "LEGACY", reason="Unused")
    info = get_deprecation(vault_dir, "LEGACY")
    assert info is not None
    assert info["replacement"] is None


def test_deprecate_key_empty_raises(vault_dir):
    with pytest.raises(ValueError):
        deprecate_key(vault_dir, "")


def test_list_deprecated_returns_keys(vault_dir):
    deprecate_key(vault_dir, "A")
    deprecate_key(vault_dir, "B")
    keys = list_deprecated(vault_dir)
    assert "A" in keys
    assert "B" in keys


def test_undeprecate_key_removes_entry(vault_dir):
    deprecate_key(vault_dir, "GONE")
    undeprecate_key(vault_dir, "GONE")
    assert "GONE" not in list_deprecated(vault_dir)


def test_undeprecate_missing_key_is_noop(vault_dir):
    undeprecate_key(vault_dir, "NONEXISTENT")  # should not raise


def test_get_deprecation_missing_returns_none(vault_dir):
    assert get_deprecation(vault_dir, "MISSING") is None


def test_check_env_for_deprecated_finds_match(vault_dir):
    deprecate_key(vault_dir, "SECRET", reason="Rotate it", replacement="SECRET_V2")
    env = {"SECRET": "abc", "OTHER": "xyz"}
    issues = check_env_for_deprecated(vault_dir, env)
    assert len(issues) == 1
    assert issues[0]["key"] == "SECRET"
    assert issues[0]["replacement"] == "SECRET_V2"


def test_check_env_for_deprecated_no_match(vault_dir):
    deprecate_key(vault_dir, "OLD")
    env = {"FRESH": "value"}
    issues = check_env_for_deprecated(vault_dir, env)
    assert issues == []


def test_check_env_for_deprecated_multiple(vault_dir):
    deprecate_key(vault_dir, "A")
    deprecate_key(vault_dir, "B")
    env = {"A": "1", "B": "2", "C": "3"}
    issues = check_env_for_deprecated(vault_dir, env)
    keys = [i["key"] for i in issues]
    assert "A" in keys
    assert "B" in keys
    assert "C" not in keys
