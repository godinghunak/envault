"""Tests for envault.commands_drift."""
import types
from pathlib import Path

import pytest

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_drift import cmd_drift


@pytest.fixture()
def vault_dir(tmp_path):
    vd = tmp_path / ".envault"
    init_vault(str(vd))
    return vd


@pytest.fixture()
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\n")
    return f


def push(vault_dir, env_file, password="secret"):
    args = types.SimpleNamespace(
        vault_dir=str(vault_dir),
        file=str(env_file),
        password=password,
    )
    cmd_push(args)


def make_args(vault_dir, env_file, password="secret", version=None, fail_on_drift=False):
    return types.SimpleNamespace(
        vault_dir=str(vault_dir),
        file=str(env_file),
        password=password,
        version=version,
        fail_on_drift=fail_on_drift,
    )


def test_cmd_drift_no_drift(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir, env_file)
    cmd_drift(args)
    out = capsys.readouterr().out
    assert "No drift" in out


def test_cmd_drift_shows_added_key(vault_dir, env_file, tmp_path, capsys):
    push(vault_dir, env_file)
    modified = tmp_path / "modified.env"
    modified.write_text("FOO=bar\nBAZ=qux\nNEW=value\n")
    args = make_args(vault_dir, modified)
    cmd_drift(args)
    out = capsys.readouterr().out
    assert "NEW" in out


def test_cmd_drift_shows_changed_value(vault_dir, env_file, tmp_path, capsys):
    push(vault_dir, env_file)
    modified = tmp_path / "modified.env"
    modified.write_text("FOO=changed\nBAZ=qux\n")
    args = make_args(vault_dir, modified)
    cmd_drift(args)
    out = capsys.readouterr().out
    assert "FOO" in out


def test_cmd_drift_missing_file_exits(vault_dir, tmp_path):
    args = make_args(vault_dir, tmp_path / "nonexistent.env")
    with pytest.raises(SystemExit):
        cmd_drift(args)


def test_cmd_drift_fail_on_drift_exits(vault_dir, env_file, tmp_path):
    push(vault_dir, env_file)
    modified = tmp_path / "modified.env"
    modified.write_text("FOO=different\n")
    args = make_args(vault_dir, modified, fail_on_drift=True)
    with pytest.raises(SystemExit):
        cmd_drift(args)
