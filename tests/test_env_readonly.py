"""Tests for envault.env_readonly."""

import pytest
from envault.env_readonly import (
    protect_key,
    unprotect_key,
    list_protected,
    is_protected,
    load_readonly,
    check_protected,
)
from envault.vault import init_vault


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path)
    init_vault(d)
    return d


def test_load_readonly_empty(vault_dir):
    data = load_readonly(vault_dir)
    assert data == {}


def test_protect_key_stores_entry(vault_dir):
    protect_key(vault_dir, "DB_PASSWORD", "Must not change in prod")
    data = load_readonly(vault_dir)
    assert "DB_PASSWORD" in data
    assert data["DB_PASSWORD"] == "Must not change in prod"


def test_protect_key_no_reason(vault_dir):
    protect_key(vault_dir, "API_KEY")
    data = load_readonly(vault_dir)
    assert data["API_KEY"] == ""


def test_protect_key_empty_raises(vault_dir):
    with pytest.raises(ValueError):
        protect_key(vault_dir, "")


def test_protect_key_overwrites_reason(vault_dir):
    protect_key(vault_dir, "SECRET", "reason one")
    protect_key(vault_dir, "SECRET", "reason two")
    assert load_readonly(vault_dir)["SECRET"] == "reason two"


def test_unprotect_key_removes_entry(vault_dir):
    protect_key(vault_dir, "FOO")
    unprotect_key(vault_dir, "FOO")
    assert "FOO" not in load_readonly(vault_dir)


def test_unprotect_missing_key_raises(vault_dir):
    with pytest.raises(KeyError):
        unprotect_key(vault_dir, "NONEXISTENT")


def test_list_protected_empty(vault_dir):
    assert list_protected(vault_dir) == []


def test_list_protected_sorted(vault_dir):
    protect_key(vault_dir, "ZEBRA")
    protect_key(vault_dir, "ALPHA")
    protect_key(vault_dir, "MANGO")
    assert list_protected(vault_dir) == ["ALPHA", "MANGO", "ZEBRA"]


def test_is_protected_true(vault_dir):
    protect_key(vault_dir, "DB_HOST")
    assert is_protected(vault_dir, "DB_HOST") is True


def test_is_protected_false(vault_dir):
    assert is_protected(vault_dir, "UNKNOWN") is False


def test_check_protected_no_base_reports_present_keys(vault_dir):
    protect_key(vault_dir, "SECRET")
    env = {"SECRET": "abc", "OTHER": "xyz"}
    violations = check_protected(vault_dir, env, base_dict=None)
    assert "SECRET" in violations
    assert "OTHER" not in violations


def test_check_protected_with_base_detects_change(vault_dir):
    protect_key(vault_dir, "SECRET")
    base = {"SECRET": "original"}
    modified = {"SECRET": "changed"}
    violations = check_protected(vault_dir, modified, base_dict=base)
    assert "SECRET" in violations


def test_check_protected_with_base_no_change_ok(vault_dir):
    protect_key(vault_dir, "SECRET")
    base = {"SECRET": "same"}
    same = {"SECRET": "same"}
    violations = check_protected(vault_dir, same, base_dict=base)
    assert violations == []
