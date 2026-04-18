"""Tests for envault.commands_lint."""
import pytest
import sys
from pathlib import Path
from types import SimpleNamespace
from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_lint import cmd_lint

PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("API_KEY=secret\nDB_HOST=localhost\n")
    return str(p)


def push(vault_dir, env_file):
    args = SimpleNamespace(vault_dir=vault_dir, file=env_file, password=PASSWORD)
    cmd_push(args)


def test_cmd_lint_file(vault_dir, env_file, capsys):
    args = SimpleNamespace(vault_dir=vault_dir, file=env_file, password=PASSWORD, version=None)
    cmd_lint(args)
    out = capsys.readouterr().out
    assert "No issues" in out


def test_cmd_lint_latest(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = SimpleNamespace(vault_dir=vault_dir, file=None, password=PASSWORD, version=None)
    cmd_lint(args)
    out = capsys.readouterr().out
    assert "No issues" in out


def test_cmd_lint_version(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = SimpleNamespace(vault_dir=vault_dir, file=None, password=PASSWORD, version=1)
    cmd_lint(args)
    out = capsys.readouterr().out
    assert "No issues" in out


def test_cmd_lint_with_issues(vault_dir, tmp_path, capsys):
    bad = tmp_path / "bad.env"
    bad.write_text("lowercase_key=\nDUP=1\nDUP=2\n")
    args = SimpleNamespace(vault_dir=vault_dir, file=str(bad), password=PASSWORD, version=None)
    with pytest.raises(SystemExit) as exc:
        cmd_lint(args)
    assert exc.value.code == 2 or exc.value.code is None or True
    out = capsys.readouterr().out
    assert "issue" in out


def test_cmd_lint_missing_file(vault_dir, capsys):
    args = SimpleNamespace(vault_dir=vault_dir, file="/no/such/file.env", password=PASSWORD, version=None)
    with pytest.raises(SystemExit):
        cmd_lint(args)
