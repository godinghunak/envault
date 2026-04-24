"""Tests for envault/env_whitelist.py"""

import pytest
from pathlib import Path

from envault.vault import init_vault
from envault.env_whitelist import (
    add_key,
    check_env,
    load_whitelist,
    remove_key,
    WhitelistViolation,
)


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


def test_load_whitelist_empty(vault_dir):
    assert load_whitelist(vault_dir) == []


def test_add_key_stores_key(vault_dir):
    add_key(vault_dir, "DB_HOST")
    assert "DB_HOST" in load_whitelist(vault_dir)


def test_add_key_idempotent(vault_dir):
    add_key(vault_dir, "DB_HOST")
    add_key(vault_dir, "DB_HOST")
    assert load_whitelist(vault_dir).count("DB_HOST") == 1


def test_add_key_empty_raises(vault_dir):
    with pytest.raises(ValueError):
        add_key(vault_dir, "")


def test_add_multiple_keys(vault_dir):
    add_key(vault_dir, "API_KEY")
    add_key(vault_dir, "DB_URL")
    keys = load_whitelist(vault_dir)
    assert "API_KEY" in keys
    assert "DB_URL" in keys


def test_remove_key_returns_true_when_present(vault_dir):
    add_key(vault_dir, "SECRET")
    result = remove_key(vault_dir, "SECRET")
    assert result is True
    assert "SECRET" not in load_whitelist(vault_dir)


def test_remove_key_returns_false_when_absent(vault_dir):
    result = remove_key(vault_dir, "NONEXISTENT")
    assert result is False


def test_check_env_empty_whitelist_no_violations(vault_dir):
    env = {"DB_HOST": "localhost", "PORT": "5432"}
    violations = check_env(vault_dir, env)
    assert violations == []


def test_check_env_all_allowed(vault_dir):
    add_key(vault_dir, "DB_HOST")
    add_key(vault_dir, "PORT")
    env = {"DB_HOST": "localhost", "PORT": "5432"}
    violations = check_env(vault_dir, env)
    assert violations == []


def test_check_env_detects_unlisted_key(vault_dir):
    add_key(vault_dir, "DB_HOST")
    env = {"DB_HOST": "localhost", "SECRET_TOKEN": "abc"}
    violations = check_env(vault_dir, env)
    assert len(violations) == 1
    assert violations[0].key == "SECRET_TOKEN"


def test_check_env_multiple_violations(vault_dir):
    add_key(vault_dir, "ONLY_KEY")
    env = {"ONLY_KEY": "ok", "EXTRA_A": "1", "EXTRA_B": "2"}
    violations = check_env(vault_dir, env)
    assert len(violations) == 2
    violation_keys = {v.key for v in violations}
    assert violation_keys == {"EXTRA_A", "EXTRA_B"}


def test_whitelist_violation_str():
    v = WhitelistViolation("MY_KEY")
    assert "MY_KEY" in str(v)
