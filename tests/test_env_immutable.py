"""Tests for envault.env_immutable."""

from __future__ import annotations

import pytest

from envault.env_immutable import (
    assert_mutable,
    is_immutable,
    list_immutable,
    load_immutable,
    lock_version,
    unlock_version,
)
from envault.vault import init_vault


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


def test_load_immutable_empty(vault_dir):
    assert load_immutable(vault_dir) == {}


def test_lock_version_stores_record(vault_dir):
    lock_version(vault_dir, 1, "do not touch")
    records = load_immutable(vault_dir)
    assert 1 in records
    assert records[1] == "do not touch"


def test_lock_version_no_reason(vault_dir):
    lock_version(vault_dir, 2)
    assert load_immutable(vault_dir)[2] == ""


def test_is_immutable_true_after_lock(vault_dir):
    lock_version(vault_dir, 3)
    assert is_immutable(vault_dir, 3) is True


def test_is_immutable_false_when_not_locked(vault_dir):
    assert is_immutable(vault_dir, 99) is False


def test_unlock_version_removes_lock(vault_dir):
    lock_version(vault_dir, 4)
    unlock_version(vault_dir, 4)
    assert is_immutable(vault_dir, 4) is False


def test_unlock_nonexistent_version_is_noop(vault_dir):
    unlock_version(vault_dir, 999)  # should not raise
    assert is_immutable(vault_dir, 999) is False


def test_list_immutable_sorted(vault_dir):
    lock_version(vault_dir, 5)
    lock_version(vault_dir, 2)
    lock_version(vault_dir, 8)
    assert list_immutable(vault_dir) == [2, 5, 8]


def test_list_immutable_empty(vault_dir):
    assert list_immutable(vault_dir) == []


def test_assert_mutable_passes_for_unlocked(vault_dir):
    assert_mutable(vault_dir, 1)  # should not raise


def test_assert_mutable_raises_for_locked(vault_dir):
    lock_version(vault_dir, 7, "frozen release")
    with pytest.raises(ValueError, match="immutable"):
        assert_mutable(vault_dir, 7)


def test_assert_mutable_error_includes_reason(vault_dir):
    lock_version(vault_dir, 10, "production tag")
    with pytest.raises(ValueError, match="production tag"):
        assert_mutable(vault_dir, 10)


def test_lock_version_overwrites_reason(vault_dir):
    lock_version(vault_dir, 1, "first reason")
    lock_version(vault_dir, 1, "updated reason")
    assert load_immutable(vault_dir)[1] == "updated reason"
