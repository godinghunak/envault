"""Tests for env_decrypt_all module."""

import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_decrypt_all import (
    decrypt_all_versions,
    decrypt_version,
    list_decryptable_versions,
)
import argparse


PASSWORD = "testpassword"


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / "vault")
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\nFOO=bar\n")
    return str(f)


def push(vault_dir, env_file, password=PASSWORD):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def test_decrypt_all_empty_vault(vault_dir):
    result = decrypt_all_versions(vault_dir, PASSWORD)
    assert result == []


def test_decrypt_all_returns_plaintext(vault_dir, env_file):
    push(vault_dir, env_file)
    results = decrypt_all_versions(vault_dir, PASSWORD)
    assert len(results) == 1
    version, plaintext = results[0]
    assert version == 1
    assert "KEY=value" in plaintext


def test_decrypt_all_multiple_versions(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    f2 = tmp_path / ".env2"
    f2.write_text("KEY=updated\n")
    push(vault_dir, str(f2))
    results = decrypt_all_versions(vault_dir, PASSWORD)
    assert len(results) == 2
    assert results[0][0] == 1
    assert results[1][0] == 2


def test_decrypt_version_specific(vault_dir, env_file):
    push(vault_dir, env_file)
    plaintext = decrypt_version(vault_dir, 1, PASSWORD)
    assert "KEY=value" in plaintext


def test_decrypt_version_not_found(vault_dir):
    with pytest.raises(FileNotFoundError):
        decrypt_version(vault_dir, 99, PASSWORD)


def test_list_decryptable_versions(vault_dir, env_file):
    push(vault_dir, env_file)
    versions = list_decryptable_versions(vault_dir, PASSWORD)
    assert versions == [1]


def test_list_decryptable_wrong_password(vault_dir, env_file):
    push(vault_dir, env_file)
    versions = list_decryptable_versions(vault_dir, "wrongpassword")
    assert versions == []
