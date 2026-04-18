"""Tests for envault/import_env.py"""
import os
import pytest
from pathlib import Path

from envault.import_env import import_from_file, import_from_string, import_from_env
from envault.vault import init_vault, list_versions
from envault.export import export_version

PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / ".envault")
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\n")
    return str(f)


def test_import_from_file_creates_version(vault_dir, env_file):
    version = import_from_file(vault_dir, env_file, PASSWORD)
    assert version == 1
    versions = list_versions(vault_dir)
    assert len(versions) == 1


def test_import_from_file_content_roundtrip(vault_dir, env_file):
    version = import_from_file(vault_dir, env_file, PASSWORD)
    content = export_version(vault_dir, version, PASSWORD)
    assert "FOO=bar" in content
    assert "BAZ=qux" in content


def test_import_from_file_not_found(vault_dir):
    with pytest.raises(FileNotFoundError):
        import_from_file(vault_dir, "/nonexistent/.env", PASSWORD)


def test_import_from_string(vault_dir):
    version = import_from_string(vault_dir, "KEY=value\n", PASSWORD)
    assert version == 1
    content = export_version(vault_dir, version, PASSWORD)
    assert "KEY=value" in content


def test_import_from_string_strict_invalid(vault_dir):
    with pytest.raises(ValueError, match="Lint"):
        import_from_string(vault_dir, "NOEQUALSSIGN\n", PASSWORD, strict=True)


def test_import_from_string_strict_valid(vault_dir):
    version = import_from_string(vault_dir, "GOOD=value\n", PASSWORD, strict=True)
    assert version == 1


def test_import_from_env(vault_dir, monkeypatch):
    monkeypatch.setenv("ENVAULT_TEST_KEY", "hello")
    version = import_from_env(vault_dir, ["ENVAULT_TEST_KEY"], PASSWORD)
    content = export_version(vault_dir, version, PASSWORD)
    assert "ENVAULT_TEST_KEY=hello" in content


def test_import_from_env_missing_keys(vault_dir, monkeypatch):
    monkeypatch.delenv("MISSING_KEY", raising=False)
    version = import_from_env(vault_dir, ["MISSING_KEY"], PASSWORD)
    content = export_version(vault_dir, version, PASSWORD)
    assert "MISSING_KEY" not in content
