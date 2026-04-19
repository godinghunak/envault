"""Tests for envault.env_lock."""
import pytest
from pathlib import Path
from envault.vault import init_vault, save_manifest, load_manifest
from envault.export import export_version
from envault.env_lock import write_lock, read_lock, verify_lock, _checksum

PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path)
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_URL=postgres://localhost/db\nSECRET=abc123\n")
    return str(f)


def push(vault_dir, env_file, password=PASSWORD):
    from envault.vault import add_version
    with open(env_file) as fh:
        content = fh.read()
    add_version(vault_dir, content, password)


def test_write_lock_creates_file(vault_dir, env_file):
    push(vault_dir, env_file)
    write_lock(vault_dir)
    from envault.env_lock import _lock_path
    assert _lock_path(vault_dir).exists()


def test_write_lock_records_version(vault_dir, env_file):
    push(vault_dir, env_file)
    lock = write_lock(vault_dir)
    assert lock["version"] == 1


def test_write_lock_records_keys(vault_dir, env_file):
    push(vault_dir, env_file)
    lock = write_lock(vault_dir)
    assert "DB_URL" in lock["keys"]
    assert "SECRET" in lock["keys"]


def test_read_lock_roundtrip(vault_dir, env_file):
    push(vault_dir, env_file)
    written = write_lock(vault_dir)
    read = read_lock(vault_dir)
    assert written["checksum"] == read["checksum"]
    assert written["version"] == read["version"]


def test_read_lock_missing_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        read_lock(vault_dir)


def test_write_lock_invalid_version_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    with pytest.raises(ValueError):
        write_lock(vault_dir, version=99)


def test_verify_lock_passes(vault_dir, env_file):
    push(vault_dir, env_file)
    write_lock(vault_dir)
    assert verify_lock(vault_dir, PASSWORD) is True


def test_checksum_deterministic():
    assert _checksum("hello") == _checksum("hello")
    assert _checksum("hello") != _checksum("world")
