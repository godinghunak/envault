"""Integration tests for commands_variables."""

import argparse
import pytest
from pathlib import Path

from envault.vault import init_vault
from envault.commands import cmd_push
from envault.commands_variables import cmd_vars_resolve, cmd_vars_check, cmd_vars_list


@pytest.fixture
def vault_dir(tmp_path):
    d = tmp_path / ".envault"
    init_vault(str(d))
    return d


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    return f


def push(vault_dir, env_file, content, password="secret"):
    env_file.write_text(content)
    ns = argparse.Namespace(
        vault_dir=str(vault_dir),
        env_file=str(env_file),
        password=password,
    )
    cmd_push(ns)


def make_args(vault_dir, **kwargs):
    base = argparse.Namespace(
        vault_dir=str(vault_dir),
        version=None,
        lenient=False,
    )
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base


def test_cmd_vars_list_no_refs(vault_dir, env_file, capsys):
    push(vault_dir, env_file, "HOST=localhost\nPORT=5432\n")
    cmd_vars_list(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "No variable references found" in out


def test_cmd_vars_list_finds_refs(vault_dir, env_file, capsys):
    push(vault_dir, env_file, "HOST=localhost\nURL=http://${HOST}/api\n")
    cmd_vars_list(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "URL" in out
    assert "HOST" in out


def test_cmd_vars_check_all_ok(vault_dir, env_file, capsys):
    push(vault_dir, env_file, "HOST=localhost\nURL=http://${HOST}\n")
    cmd_vars_check(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "resolvable" in out.lower()


def test_cmd_vars_check_unresolved(vault_dir, env_file, capsys):
    push(vault_dir, env_file, "URL=http://${UNDEFINED_HOST}\n")
    cmd_vars_check(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "URL" in out
    assert "UNDEFINED_HOST" in out


def test_cmd_vars_resolve_expands(vault_dir, env_file, capsys):
    push(vault_dir, env_file, "HOST=localhost\nURL=http://${HOST}\n")
    cmd_vars_resolve(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "URL=http://localhost" in out


def test_cmd_vars_resolve_strict_error(vault_dir, env_file, capsys):
    push(vault_dir, env_file, "URL=http://${GHOST}\n")
    cmd_vars_resolve(make_args(vault_dir, lenient=False))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_vars_resolve_lenient_keeps_ref(vault_dir, env_file, capsys):
    push(vault_dir, env_file, "URL=http://${GHOST}\n")
    cmd_vars_resolve(make_args(vault_dir, lenient=True))
    out = capsys.readouterr().out
    assert "${GHOST}" in out
