import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_snapshot import (
    create_snapshot, get_snapshot, delete_snapshot, list_snapshots
)
import argparse

PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\nFOO=bar\n")
    return str(f)


def push(vault_dir, env_file, password=PASSWORD):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def test_list_snapshots_empty(vault_dir):
    assert list_snapshots(vault_dir) == []


def test_create_snapshot_no_versions_raises(vault_dir):
    with pytest.raises(ValueError, match="No versions"):
        create_snapshot(vault_dir, "snap1", PASSWORD)


def test_create_snapshot_returns_version(vault_dir, env_file):
    push(vault_dir, env_file)
    v = create_snapshot(vault_dir, "snap1", PASSWORD)
    assert v == 1


def test_list_snapshots_after_create(vault_dir, env_file):
    push(vault_dir, env_file)
    create_snapshot(vault_dir, "snap1", PASSWORD)
    assert "snap1" in list_snapshots(vault_dir)


def test_get_snapshot_content(vault_dir, env_file):
    push(vault_dir, env_file)
    create_snapshot(vault_dir, "mysnap", PASSWORD)
    snap = get_snapshot(vault_dir, "mysnap")
    assert snap["version"] == 1
    assert "KEY=value" in snap["content"]
    assert "created_at" in snap


def test_get_snapshot_missing_raises(vault_dir):
    with pytest.raises(KeyError, match="ghost"):
        get_snapshot(vault_dir, "ghost")


def test_delete_snapshot(vault_dir, env_file):
    push(vault_dir, env_file)
    create_snapshot(vault_dir, "snap1", PASSWORD)
    delete_snapshot(vault_dir, "snap1")
    assert "snap1" not in list_snapshots(vault_dir)


def test_delete_missing_snapshot_raises(vault_dir):
    with pytest.raises(KeyError):
        delete_snapshot(vault_dir, "nope")


def test_create_snapshot_specific_version(vault_dir, env_file):
    push(vault_dir, env_file)
    env_file2 = Path(env_file)
    env_file2.write_text("KEY=changed\n")
    push(vault_dir, env_file, PASSWORD)
    v = create_snapshot(vault_dir, "old", PASSWORD, version=1)
    assert v == 1
    snap = get_snapshot(vault_dir, "old")
    assert "KEY=value" in snap["content"]
