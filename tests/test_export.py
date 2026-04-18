"""Tests for envault.export and commands_export."""
import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.export import export_version, export_latest, export_to_file

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


def push(vault_dir, env_file):
    import argparse
    args = argparse.Namespace(vault_dir=vault_dir, env_file=env_file, password=PASSWORD)
    cmd_push(args)


def test_export_latest_returns_content(vault_dir, env_file):
    push(vault_dir, env_file)
    content = export_latest(vault_dir, PASSWORD)
    assert "KEY=value" in content
    assert "FOO=bar" in content


def test_export_version_returns_content(vault_dir, env_file):
    push(vault_dir, env_file)
    content = export_version(vault_dir, 1, PASSWORD)
    assert "KEY=value" in content


def test_export_wrong_password_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    with pytest.raises(Exception):
        export_version(vault_dir, 1, "wrongpass")


def test_export_missing_version_raises(vault_dir, env_file):
    push(vault_dir, env_file)
    with pytest.raises(ValueError, match="Version 99 not found"):
        export_version(vault_dir, 99, PASSWORD)


def test_export_no_versions_raises(vault_dir):
    with pytest.raises(ValueError, match="No versions found"):
        export_latest(vault_dir, PASSWORD)


def test_export_to_file_writes_content(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    out = str(tmp_path / "out.env")
    export_to_file(vault_dir, 1, PASSWORD, out)
    content = Path(out).read_text()
    assert "KEY=value" in content


def test_export_multiple_versions(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    env2 = tmp_path / ".env2"
    env2.write_text("KEY=changed\nNEW=yes\n")
    push(vault_dir, str(env2))
    c1 = export_version(vault_dir, 1, PASSWORD)
    c2 = export_version(vault_dir, 2, PASSWORD)
    assert "KEY=value" in c1
    assert "KEY=changed" in c2
