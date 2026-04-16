"""Integration tests for high-level envault commands."""

import pytest
from pathlib import Path

from envault.commands import cmd_init, cmd_push, cmd_pull, cmd_list


PASSWORD = "s3cr3t!"


@pytest.fixture()
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("API_KEY=abc123\nDEBUG=true\n")
    return str(f)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path / ".envault")


def test_cmd_init(vault_dir):
    msg = cmd_init(vault_dir)
    assert "initialized" in msg.lower()
    assert Path(vault_dir).is_dir()


def test_cmd_push_creates_encrypted_file(env_file, vault_dir):
    msg = cmd_push(env_file, PASSWORD, vault_dir=vault_dir)
    assert "version 1" in msg
    assert (Path(vault_dir) / "env_v1.enc").exists()


def test_cmd_push_increments_version(env_file, vault_dir):
    cmd_push(env_file, PASSWORD, vault_dir=vault_dir)
    msg = cmd_push(env_file, PASSWORD, vault_dir=vault_dir)
    assert "version 2" in msg


def test_cmd_pull_restores_content(env_file, tmp_path, vault_dir):
    cmd_push(env_file, PASSWORD, vault_dir=vault_dir)
    output = str(tmp_path / "restored.env")
    msg = cmd_pull(output, PASSWORD, vault_dir=vault_dir)
    assert "version 1" in msg
    assert Path(output).read_text() == Path(env_file).read_text()


def test_cmd_pull_specific_version(env_file, tmp_path, vault_dir):
    cmd_push(env_file, PASSWORD, label="v1", vault_dir=vault_dir)
    Path(env_file).write_text("UPDATED=yes\n")
    cmd_push(env_file, PASSWORD, label="v2", vault_dir=vault_dir)

    output = str(tmp_path / "old.env")
    cmd_pull(output, PASSWORD, version_id=1, vault_dir=vault_dir)
    assert "API_KEY=abc123" in Path(output).read_text()


def test_cmd_pull_wrong_password_raises(env_file, tmp_path, vault_dir):
    cmd_push(env_file, PASSWORD, vault_dir=vault_dir)
    output = str(tmp_path / "out.env")
    with pytest.raises(Exception):
        cmd_pull(output, "wrongpassword", vault_dir=vault_dir)


def test_cmd_list_returns_versions(env_file, vault_dir):
    cmd_push(env_file, PASSWORD, label="alpha", vault_dir=vault_dir)
    cmd_push(env_file, PASSWORD, label="beta", vault_dir=vault_dir)
    versions = cmd_list(vault_dir)
    assert len(versions) == 2
    assert versions[0]["label"] == "alpha"
    assert versions[1]["label"] == "beta"
