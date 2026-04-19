"""Tests for env_clone module."""
import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_clone import clone_version_to_file, clone_latest_to_file, list_clone_targets
import argparse


PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    vd = str(tmp_path / ".envault")
    init_vault(vd)
    return vd


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\nFOO=bar\n")
    return str(f)


def push(vault_dir, env_file, password=PASSWORD):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def test_list_clone_targets_empty(vault_dir):
    assert list_clone_targets(vault_dir) == []


def test_list_clone_targets_after_push(vault_dir, env_file):
    push(vault_dir, env_file)
    push(vault_dir, env_file)
    targets = list_clone_targets(vault_dir)
    assert targets == [1, 2]


def test_clone_latest_creates_file(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    dest = str(tmp_path / "out.env")
    version = clone_latest_to_file(vault_dir, dest, PASSWORD)
    assert version == 1
    assert Path(dest).exists()
    assert "KEY=value" in Path(dest).read_text()


def test_clone_version_creates_file(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    dest = str(tmp_path / "out.env")
    version = clone_version_to_file(vault_dir, 1, dest, PASSWORD)
    assert version == 1
    content = Path(dest).read_text()
    assert "FOO=bar" in content


def test_clone_invalid_version_raises(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    dest = str(tmp_path / "out.env")
    with pytest.raises(ValueError, match="not found"):
        clone_version_to_file(vault_dir, 99, dest, PASSWORD)


def test_clone_empty_vault_raises(vault_dir, tmp_path):
    dest = str(tmp_path / "out.env")
    with pytest.raises(ValueError, match="No versions"):
        clone_latest_to_file(vault_dir, dest, PASSWORD)
