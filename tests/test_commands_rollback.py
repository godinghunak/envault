"""Tests for rollback CLI command handlers."""

import os
import pytest
from types import SimpleNamespace
from envault.vault import init_vault, push_version
from envault.commands_rollback import cmd_rollback, cmd_versions


PASSWORD = "secret"
ENV_CONTENT = b"KEY=value\nFOO=bar\n"


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / "vault")
    init_vault(d)
    return d


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_bytes(ENV_CONTENT)
    return str(p)


def make_args(**kwargs):
    defaults = {"vault_dir": None, "name": ".env", "version": 1,
                "output": None, "password": PASSWORD}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_versions_empty(vault_dir, capsys):
    args = make_args(vault_dir=vault_dir)
    cmd_versions(args)
    out = capsys.readouterr().out
    assert "No versions found" in out


def test_cmd_versions_lists(vault_dir, env_file, capsys):
    push_version(vault_dir, ".env", env_file, PASSWORD)
    push_version(vault_dir, ".env", env_file, PASSWORD)
    args = make_args(vault_dir=vault_dir)
    cmd_versions(args)
    out = capsys.readouterr().out
    assert "v1" in out
    assert "v2" in out


def test_cmd_rollback_creates_file(vault_dir, env_file, tmp_path):
    push_version(vault_dir, ".env", env_file, PASSWORD)
    output = str(tmp_path / "restored.env")
    args = make_args(vault_dir=vault_dir, version=1, output=output)
    cmd_rollback(args)
    assert os.path.exists(output)
    assert open(output, "rb").read() == ENV_CONTENT


def test_cmd_rollback_bad_version_exits(vault_dir, env_file):
    push_version(vault_dir, ".env", env_file, PASSWORD)
    args = make_args(vault_dir=vault_dir, version=42, output="/tmp/x.env")
    with pytest.raises(SystemExit):
        cmd_rollback(args)
