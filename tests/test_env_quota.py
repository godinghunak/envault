"""Tests for envault.env_quota."""

import pytest
from envault.vault import init_vault
from envault.env_quota import (
    load_quota, set_quota, get_quota, clear_quota,
    check_quota, enforce_quota, DEFAULT_MAX_VERSIONS,
)


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


def test_load_quota_empty(vault_dir):
    assert load_quota(vault_dir) == {}


def test_get_quota_returns_default(vault_dir):
    assert get_quota(vault_dir) == DEFAULT_MAX_VERSIONS


def test_set_quota_stores_value(vault_dir):
    set_quota(vault_dir, 10)
    assert get_quota(vault_dir) == 10


def test_set_quota_invalid_raises(vault_dir):
    with pytest.raises(ValueError):
        set_quota(vault_dir, 0)


def test_set_quota_negative_raises(vault_dir):
    with pytest.raises(ValueError):
        set_quota(vault_dir, -5)


def test_clear_quota_restores_default(vault_dir):
    set_quota(vault_dir, 3)
    clear_quota(vault_dir)
    assert get_quota(vault_dir) == DEFAULT_MAX_VERSIONS


def test_check_quota_within(vault_dir):
    set_quota(vault_dir, 5)
    ok, max_v = check_quota(vault_dir, 4)
    assert ok is True
    assert max_v == 5


def test_check_quota_at_limit(vault_dir):
    set_quota(vault_dir, 5)
    ok, _ = check_quota(vault_dir, 5)
    assert ok is False


def test_enforce_quota_passes(vault_dir):
    set_quota(vault_dir, 10)
    enforce_quota(vault_dir, 9)  # should not raise


def test_enforce_quota_raises_when_exceeded(vault_dir):
    set_quota(vault_dir, 3)
    with pytest.raises(RuntimeError, match="Quota exceeded"):
        enforce_quota(vault_dir, 3)
