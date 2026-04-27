"""Tests for envault.env_retention."""
from __future__ import annotations

import pytest

from envault.env_retention import (
    apply_retention,
    clear_policy,
    get_policy,
    set_policy,
)
from envault.vault import init_vault


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


def test_get_policy_empty(vault_dir):
    assert get_policy(vault_dir) is None


def test_set_policy_stores_values(vault_dir):
    set_policy(vault_dir, max_versions=5, min_keep=2)
    policy = get_policy(vault_dir)
    assert policy is not None
    assert policy["max_versions"] == 5
    assert policy["min_keep"] == 2


def test_set_policy_default_min_keep(vault_dir):
    set_policy(vault_dir, max_versions=3)
    policy = get_policy(vault_dir)
    assert policy["min_keep"] == 1


def test_set_policy_invalid_max_versions_raises(vault_dir):
    with pytest.raises(ValueError, match="max_versions"):
        set_policy(vault_dir, max_versions=0)


def test_set_policy_invalid_min_keep_raises(vault_dir):
    with pytest.raises(ValueError, match="min_keep"):
        set_policy(vault_dir, max_versions=5, min_keep=0)


def test_set_policy_min_keep_exceeds_max_raises(vault_dir):
    with pytest.raises(ValueError, match="min_keep cannot exceed"):
        set_policy(vault_dir, max_versions=3, min_keep=5)


def test_clear_policy_removes_config(vault_dir):
    set_policy(vault_dir, max_versions=4)
    clear_policy(vault_dir)
    assert get_policy(vault_dir) is None


def test_clear_policy_idempotent(vault_dir):
    clear_policy(vault_dir)  # should not raise


def test_apply_retention_no_policy_returns_empty(vault_dir):
    result = apply_retention(vault_dir, [1, 2, 3, 4, 5])
    assert result == []


def test_apply_retention_prunes_oldest(vault_dir):
    set_policy(vault_dir, max_versions=3, min_keep=1)
    result = apply_retention(vault_dir, [1, 2, 3, 4, 5])
    assert result == [1, 2]


def test_apply_retention_keeps_minimum(vault_dir):
    set_policy(vault_dir, max_versions=2, min_keep=2)
    result = apply_retention(vault_dir, [1, 2, 3, 4])
    pruned = result
    assert 3 not in pruned
    assert 4 not in pruned


def test_apply_retention_fewer_versions_than_max(vault_dir):
    set_policy(vault_dir, max_versions=10, min_keep=1)
    result = apply_retention(vault_dir, [1, 2, 3])
    assert result == []
