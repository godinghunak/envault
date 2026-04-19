"""Tests for env_rotate module."""

import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_rotate import rotate_password, rotate_single_version
from envault.crypto import decrypt_file
from envault.vault import _vault_path
import argparse


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("KEY=value\nSECRET=abc123\n")
    return str(p)


def push(vault_dir, env_file, password="pass"):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def test_rotate_password_all_versions(vault_dir, env_file):
    push(vault_dir, env_file, "oldpass")
    push(vault_dir, env_file, "oldpass")

    rotated = rotate_password(vault_dir, "oldpass", "newpass")
    assert rotated == [1, 2]


def test_rotated_version_decryptable_with_new_password(vault_dir, env_file):
    push(vault_dir, env_file, "oldpass")
    rotate_password(vault_dir, "oldpass", "newpass")

    enc = str(Path(_vault_path(vault_dir)) / "v1.env.enc")
    content = decrypt_file(enc, "newpass")
    assert b"KEY=value" in content


def test_rotated_version_not_decryptable_with_old_password(vault_dir, env_file):
    push(vault_dir, env_file, "oldpass")
    rotate_password(vault_dir, "oldpass", "newpass")

    enc = str(Path(_vault_path(vault_dir)) / "v1.env.enc")
    with pytest.raises(Exception):
        decrypt_file(enc, "oldpass")


def test_rotate_empty_vault_returns_empty(vault_dir):
    result = rotate_password(vault_dir, "any", "other")
    assert result == []


def test_rotate_single_version(vault_dir, env_file):
    push(vault_dir, env_file, "oldpass")
    push(vault_dir, env_file, "oldpass")

    ok = rotate_single_version(vault_dir, 1, "oldpass", "newpass")
    assert ok is True

    enc1 = str(Path(_vault_path(vault_dir)) / "v1.env.enc")
    enc2 = str(Path(_vault_path(vault_dir)) / "v2.env.enc")
    assert b"KEY=value" in decrypt_file(enc1, "newpass")
    assert b"KEY=value" in decrypt_file(enc2, "oldpass")


def test_rotate_single_version_not_found(vault_dir):
    with pytest.raises(FileNotFoundError):
        rotate_single_version(vault_dir, 99, "old", "new")
