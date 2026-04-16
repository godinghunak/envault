"""Tests for vault manifest management."""

import json
import pytest
from pathlib import Path

from envault import vault


@pytest.fixture()
def tmp_vault(tmp_path):
    vault_dir = str(tmp_path / ".envault")
    vault.init_vault(vault_dir)
    return vault_dir


def test_init_creates_directory(tmp_path):
    vault_dir = str(tmp_path / ".envault")
    vault.init_vault(vault_dir)
    assert Path(vault_dir).is_dir()


def test_init_creates_manifest(tmp_vault):
    manifest_file = Path(tmp_vault) / "manifest.json"
    assert manifest_file.exists()
    data = json.loads(manifest_file.read_text())
    assert data == {"versions": []}


def test_init_idempotent(tmp_vault):
    vault.init_vault(tmp_vault)  # second init should not raise
    assert vault.list_versions(tmp_vault) == []


def test_add_and_list_versions(tmp_vault):
    entry = vault.add_version("env_v1.enc", label="first", vault_dir=tmp_vault)
    assert entry["id"] == 1
    assert entry["label"] == "first"
    versions = vault.list_versions(tmp_vault)
    assert len(versions) == 1


def test_get_version(tmp_vault):
    vault.add_version("env_v1.enc", vault_dir=tmp_vault)
    vault.add_version("env_v2.enc", vault_dir=tmp_vault)
    v = vault.get_version(2, vault_dir=tmp_vault)
    assert v["file"] == "env_v2.enc"


def test_get_version_missing_raises(tmp_vault):
    with pytest.raises(KeyError):
        vault.get_version(99, vault_dir=tmp_vault)


def test_latest_version_none_when_empty(tmp_vault):
    assert vault.latest_version(tmp_vault) is None


def test_latest_version_returns_last(tmp_vault):
    vault.add_version("env_v1.enc", vault_dir=tmp_vault)
    vault.add_version("env_v2.enc", vault_dir=tmp_vault)
    latest = vault.latest_version(tmp_vault)
    assert latest["id"] == 2


def test_load_manifest_no_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        vault.load_manifest(str(tmp_path / "nonexistent"))
