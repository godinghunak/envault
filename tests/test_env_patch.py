import pytest
from pathlib import Path
from envault.vault import init_vault, load_manifest
from envault.commands import cmd_push
from envault.env_patch import patch_version, patch_latest
from envault.export import export_latest, export_version
import types

PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / ".envault")
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\nSECRET=abc\n")
    return str(f)


def push(vault_dir, env_file):
    args = types.SimpleNamespace(vault_dir=vault_dir, env_file=env_file, password=PASSWORD)
    cmd_push(args)


def test_patch_latest_updates_key(vault_dir, env_file):
    push(vault_dir, env_file)
    new_ver = patch_latest(vault_dir, PASSWORD, {"FOO": "newval"})
    content = export_version(vault_dir, new_ver, PASSWORD).decode()
    assert "FOO=newval" in content
    assert "BAZ=qux" in content


def test_patch_latest_removes_key(vault_dir, env_file):
    push(vault_dir, env_file)
    new_ver = patch_latest(vault_dir, PASSWORD, {}, removals=["SECRET"])
    content = export_version(vault_dir, new_ver, PASSWORD).decode()
    assert "SECRET" not in content
    assert "FOO=bar" in content


def test_patch_version_specific(vault_dir, env_file):
    push(vault_dir, env_file)
    push(vault_dir, env_file)  # version 2
    new_ver = patch_version(vault_dir, PASSWORD, 1, {"FOO": "patched"})
    content = export_version(vault_dir, new_ver, PASSWORD).decode()
    assert "FOO=patched" in content


def test_patch_empty_vault_raises(vault_dir):
    with pytest.raises(ValueError, match="No versions"):
        patch_latest(vault_dir, PASSWORD, {"X": "1"})


def test_patch_invalid_version_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    with pytest.raises(ValueError, match="does not exist"):
        patch_version(vault_dir, PASSWORD, 99, {"X": "1"})


def test_patch_creates_new_version(vault_dir, env_file):
    push(vault_dir, env_file)
    manifest_before = load_manifest(vault_dir)
    count_before = len(manifest_before["versions"])
    patch_latest(vault_dir, PASSWORD, {"NEW_KEY": "hello"})
    manifest_after = load_manifest(vault_dir)
    assert len(manifest_after["versions"]) == count_before + 1
