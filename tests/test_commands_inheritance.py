"""Tests for envault.commands_inheritance."""
from __future__ import annotations

import os
import pytest
from argparse import Namespace

from envault.vault import init_vault
from envault.commands import cmd_push


@pytest.fixture()
def vault_dir(tmp_path):
    vd = str(tmp_path / ".envault")
    init_vault(vd)
    return vd


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("HOST=localhost\nPORT=5432\nDB=prod\n")
    return str(p)


def push(vault_dir, env_file, password="secret"):
    args = Namespace(
        vault_dir=vault_dir,
        env_file=env_file,
        password=password,
    )
    cmd_push(args)


def make_args(vault_dir, **kwargs):
    defaults = dict(
        vault_dir=vault_dir,
        password="secret",
        parent=1,
        child=None,
        exclude=None,
        summary=False,
        verbose=False,
    )
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_cmd_inherit_prints_merged_keys(vault_dir, env_file, tmp_path, capsys):
    push(vault_dir, env_file)
    child_env = tmp_path / ".env2"
    child_env.write_text("HOST=staging.example.com\nDEBUG=true\n")
    push(vault_dir, str(child_env))

    from envault.commands_inheritance import cmd_inherit
    args = make_args(vault_dir, parent=1, child=2)
    cmd_inherit(args)
    out = capsys.readouterr().out
    assert "HOST=staging.example.com" in out
    assert "PORT=5432" in out
    assert "DEBUG=true" in out


def test_cmd_inherit_summary_flag(vault_dir, env_file, tmp_path, capsys):
    push(vault_dir, env_file)
    child_env = tmp_path / ".env2"
    child_env.write_text("HOST=staging.example.com\n")
    push(vault_dir, str(child_env))

    from envault.commands_inheritance import cmd_inherit
    args = make_args(vault_dir, parent=1, child=2, summary=True)
    cmd_inherit(args)
    out = capsys.readouterr().out
    assert "Merged keys" in out
    assert "Inherited" in out


def test_cmd_inherit_verbose_shows_origin(vault_dir, env_file, tmp_path, capsys):
    push(vault_dir, env_file)
    child_env = tmp_path / ".env2"
    child_env.write_text("HOST=staging.example.com\n")
    push(vault_dir, str(child_env))

    from envault.commands_inheritance import cmd_inherit
    args = make_args(vault_dir, parent=1, child=2, verbose=True)
    cmd_inherit(args)
    out = capsys.readouterr().out
    assert "(overridden)" in out or "(parent)" in out or "(child-only)" in out


def test_cmd_inherit_exclude_removes_key(vault_dir, env_file, tmp_path, capsys):
    push(vault_dir, env_file)
    child_env = tmp_path / ".env2"
    child_env.write_text("HOST=staging.example.com\n")
    push(vault_dir, str(child_env))

    from envault.commands_inheritance import cmd_inherit
    args = make_args(vault_dir, parent=1, child=2, exclude=["PORT"])
    cmd_inherit(args)
    out = capsys.readouterr().out
    assert "PORT" not in out
