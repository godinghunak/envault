"""Tests for env_backup module."""

import pytest
import tarfile
from pathlib import Path

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_backup import create_backup, restore_backup, backup_info


@pytest.fixture
def vault_dir(tmp_path):
    vd = str(tmp_path / ".envault")
    init_vault(vd)
    return vd


@pytest.fixture
def env_file(tmp_path):
    ef = tmp_path / ".env"
    ef.write_text("KEY=value\nSECRET=abc123\n")
    return str(ef)


def push(vault_dir, env_file, password="pass"):
    import argparse
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def test_create_backup_returns_path(vault_dir, tmp_path):
    dest = str(tmp_path / "backup.tar.gz")
    result = create_backup(vault_dir, dest)
    assert result == dest
    assert Path(dest).exists()


def test_create_backup_is_valid_tar(vault_dir, tmp_path):
    dest = str(tmp_path / "backup.tar.gz")
    create_backup(vault_dir, dest)
    assert tarfile.is_tarfile(dest)


def test_create_backup_missing_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        create_backup(str(tmp_path / "nonexistent"), str(tmp_path / "out.tar.gz"))


def test_restore_backup_recreates_files(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    dest_backup = str(tmp_path / "backup.tar.gz")
    create_backup(vault_dir, dest_backup)

    restore_dest = str(tmp_path / "restored_vault")
    restore_backup(dest_backup, restore_dest)

    restored = Path(restore_dest)
    assert restored.exists()
    assert (restored / "manifest.json").exists()


def test_restore_backup_raises_if_exists(vault_dir, tmp_path):
    dest_backup = str(tmp_path / "backup.tar.gz")
    create_backup(vault_dir, dest_backup)

    restore_dest = str(tmp_path / "existing")
    Path(restore_dest).mkdir()

    with pytest.raises(FileExistsError):
        restore_backup(dest_backup, restore_dest, overwrite=False)


def test_restore_backup_overwrite_succeeds(vault_dir, tmp_path):
    dest_backup = str(tmp_path / "backup.tar.gz")
    create_backup(vault_dir, dest_backup)

    restore_dest = str(tmp_path / "existing")
    Path(restore_dest).mkdir()

    result = restore_backup(dest_backup, restore_dest, overwrite=True)
    assert result == restore_dest


def test_backup_info_returns_metadata(vault_dir, tmp_path):
    dest = str(tmp_path / "backup.tar.gz")
    create_backup(vault_dir, dest)
    info = backup_info(dest)
    assert "size_bytes" in info
    assert "created" in info
    assert isinstance(info["files"], list)


def test_backup_info_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        backup_info(str(tmp_path / "no_such.tar.gz"))
