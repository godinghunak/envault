"""Tests for envault/env_sign.py"""
import pytest
from pathlib import Path

from envault.vault import init_vault
from envault.env_sign import (
    sign_version, verify_version, load_signatures,
    get_signature_entry, remove_signature
)


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


FAKE_DATA = b"encrypted-payload-abc"
SECRET = "mysecret"


def test_sign_returns_hex_string(vault_dir):
    sig = sign_version(vault_dir, 1, FAKE_DATA, SECRET)
    assert isinstance(sig, str)
    assert len(sig) == 64  # SHA256 hex


def test_sign_stores_signature(vault_dir):
    sign_version(vault_dir, 1, FAKE_DATA, SECRET)
    sigs = load_signatures(vault_dir)
    assert "1" in sigs
    assert "signature" in sigs["1"]
    assert "signed_at" in sigs["1"]


def test_verify_valid_signature(vault_dir):
    sign_version(vault_dir, 1, FAKE_DATA, SECRET)
    assert verify_version(vault_dir, 1, FAKE_DATA, SECRET) is True


def test_verify_wrong_secret_fails(vault_dir):
    sign_version(vault_dir, 1, FAKE_DATA, SECRET)
    assert verify_version(vault_dir, 1, FAKE_DATA, "wrongsecret") is False


def test_verify_tampered_data_fails(vault_dir):
    sign_version(vault_dir, 1, FAKE_DATA, SECRET)
    assert verify_version(vault_dir, 1, b"tampered-data", SECRET) is False


def test_verify_missing_version_raises(vault_dir):
    with pytest.raises(KeyError):
        verify_version(vault_dir, 99, FAKE_DATA, SECRET)


def test_get_signature_entry(vault_dir):
    sign_version(vault_dir, 2, FAKE_DATA, SECRET)
    entry = get_signature_entry(vault_dir, 2)
    assert entry is not None
    assert "signature" in entry


def test_get_signature_entry_missing_returns_none(vault_dir):
    assert get_signature_entry(vault_dir, 99) is None


def test_remove_signature(vault_dir):
    sign_version(vault_dir, 1, FAKE_DATA, SECRET)
    result = remove_signature(vault_dir, 1)
    assert result is True
    assert get_signature_entry(vault_dir, 1) is None


def test_remove_signature_missing_returns_false(vault_dir):
    assert remove_signature(vault_dir, 42) is False


def test_multiple_versions(vault_dir):
    sign_version(vault_dir, 1, FAKE_DATA, SECRET)
    sign_version(vault_dir, 2, b"other-data", SECRET)
    sigs = load_signatures(vault_dir)
    assert "1" in sigs
    assert "2" in sigs
