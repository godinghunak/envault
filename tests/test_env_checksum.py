"""Tests for envault.env_checksum."""

import pytest
from pathlib import Path

from envault.vault import init_vault, load_manifest
from envault.commands import cmd_push
from envault.env_checksum import (
    compute_checksum,
    record_checksum,
    verify_checksum,
    get_checksum,
    load_checksums,
)

PASSWORD = "testpassword"


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(tmp_path)
    return tmp_path


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\nFOO=bar\n")
    return f


def push(vault_dir, env_file):
    import argparse
    args = argparse.Namespace(
        vault_dir=str(vault_dir),
        env_file=str(env_file),
        password=PASSWORD,
    )
    cmd_push(args)


def test_compute_checksum_returns_hex_string():
    result = compute_checksum(b"hello world")
    assert isinstance(result, str)
    assert len(result) == 64  # sha256 hex


def test_compute_checksum_deterministic():
    a = compute_checksum(b"data")
    b = compute_checksum(b"data")
    assert a == b


def test_compute_checksum_changes_on_different_input():
    assert compute_checksum(b"aaa") != compute_checksum(b"bbb")


def test_record_checksum_stores_entry(vault_dir, env_file):
    push(vault_dir, env_file)
    checksum = record_checksum(vault_dir, 1, PASSWORD)
    data = load_checksums(vault_dir)
    assert "1" in data
    assert data["1"]["checksum"] == checksum
    assert data["1"]["algorithm"] == "sha256"


def test_record_checksum_returns_hex_string(vault_dir, env_file):
    push(vault_dir, env_file)
    checksum = record_checksum(vault_dir, 1, PASSWORD)
    assert isinstance(checksum, str)
    assert len(checksum) == 64


def test_verify_checksum_ok(vault_dir, env_file):
    push(vault_dir, env_file)
    record_checksum(vault_dir, 1, PASSWORD)
    assert verify_checksum(vault_dir, 1, PASSWORD) is True


def test_verify_checksum_missing_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    with pytest.raises(KeyError):
        verify_checksum(vault_dir, 1, PASSWORD)


def test_get_checksum_none_when_absent(vault_dir, env_file):
    push(vault_dir, env_file)
    assert get_checksum(vault_dir, 1) is None


def test_get_checksum_returns_entry_after_record(vault_dir, env_file):
    push(vault_dir, env_file)
    record_checksum(vault_dir, 1, PASSWORD)
    entry = get_checksum(vault_dir, 1)
    assert entry is not None
    assert "checksum" in entry


def test_load_checksums_empty(vault_dir):
    assert load_checksums(vault_dir) == {}
