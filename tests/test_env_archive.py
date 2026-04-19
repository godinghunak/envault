import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.env_archive import (
    create_archive,
    list_archives,
    load_archive,
    delete_archive,
)
import argparse


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\nFOO=bar\n")
    return str(f)


def push(vault_dir, env_file, password="secret"):
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=password)
    cmd_push(args)


def test_list_archives_empty(vault_dir):
    assert list_archives(vault_dir) == []


def test_create_archive_no_versions_raises(vault_dir):
    with pytest.raises(ValueError, match="No versions"):
        create_archive(vault_dir, "backup1")


def test_create_archive_creates_file(vault_dir, env_file):
    push(vault_dir, env_file)
    path = create_archive(vault_dir, "backup1")
    assert path.exists()
    assert path.suffix == ".evarchive"


def test_list_archives_after_create(vault_dir, env_file):
    push(vault_dir, env_file)
    create_archive(vault_dir, "backup1")
    create_archive(vault_dir, "backup2")
    assert list_archives(vault_dir) == ["backup1", "backup2"]


def test_load_archive_contains_versions(vault_dir, env_file):
    push(vault_dir, env_file)
    create_archive(vault_dir, "snap")
    data = load_archive(vault_dir, "snap")
    assert "versions" in data
    assert "1" in data["versions"]


def test_load_archive_missing_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        load_archive(vault_dir, "nonexistent")


def test_create_archive_specific_versions(vault_dir, env_file):
    push(vault_dir, env_file)
    push(vault_dir, env_file)
    path = create_archive(vault_dir, "v1only", versions=[1])
    data = load_archive(vault_dir, "v1only")
    assert "1" in data["versions"]
    assert "2" not in data["versions"]


def test_create_archive_invalid_version_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    with pytest.raises(ValueError, match="does not exist"):
        create_archive(vault_dir, "bad", versions=[99])


def test_delete_archive(vault_dir, env_file):
    push(vault_dir, env_file)
    create_archive(vault_dir, "temp")
    delete_archive(vault_dir, "temp")
    assert "temp" not in list_archives(vault_dir)


def test_delete_archive_missing_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        delete_archive(vault_dir, "ghost")
