"""Integration tests for cmd_diff."""
import argparse
import pytest
from pathlib import Path
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_diff import cmd_diff


@pytest.fixture
def vault_dir(tmp_path):
    vd = str(tmp_path / ".envault")
    init_vault(vd)
    return vd


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("FOO=bar\nBAZ=qux\n")
    return str(p)


def push(vault_dir, env_file, password="pw"):
    args = argparse.Namespace(vault_dir=vault_dir, password=password)
    cmd_push(args)


def test_cmd_diff_requires_two_versions(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = argparse.Namespace(
        vault_dir=vault_dir, password="pw", v1=None, v2=None, show_values=False
    )
    cmd_diff(args)
    out = capsys.readouterr().out
    assert "Need at least 2" in out


def test_cmd_diff_shows_changes(vault_dir, tmp_path, capsys):
    env1 = tmp_path / "e1.env"
    env1.write_text("FOO=bar\n")
    push(vault_dir, str(env1))

    env2 = tmp_path / "e2.env"
    env2.write_text("FOO=bar\nNEW=value\n")
    push(vault_dir, str(env2))

    args = argparse.Namespace(
        vault_dir=vault_dir, password="pw", v1=None, v2=None, show_values=False
    )
    cmd_diff(args)
    out = capsys.readouterr().out
    assert "NEW" in out
    assert "+" in out


def test_cmd_diff_no_changes(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    push(vault_dir, env_file)
    args = argparse.Namespace(
        vault_dir=vault_dir, password="pw", v1=None, v2=None, show_values=False
    )
    cmd_diff(args)
    out = capsys.readouterr().out
    assert "no changes" in out
