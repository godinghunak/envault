"""Integration tests for envault.commands_bookmark."""

from __future__ import annotations

import pytest

from envault.commands_bookmark import (
    cmd_bookmark_add,
    cmd_bookmark_list,
    cmd_bookmark_remove,
    cmd_bookmark_resolve,
)
from envault.env_bookmark import add_bookmark, load_bookmarks
from envault.vault import init_vault
from envault.commands import cmd_push


@pytest.fixture
def vault_dir(tmp_path):
    vd = str(tmp_path / ".envault")
    init_vault(vd)
    return vd


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\nOTHER=data\n")
    return str(f)


def push(vault_dir, env_file, password="secret"):
    class A:
        pass
    a = A()
    a.vault_dir = vault_dir
    a.env_file = env_file
    a.password = password
    cmd_push(a)


def make_args(vault_dir, **kwargs):
    class A:
        pass
    a = A()
    a.vault_dir = vault_dir
    for k, v in kwargs.items():
        setattr(a, k, v)
    return a


def test_cmd_bookmark_add_prints_confirmation(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    args = make_args(vault_dir, name="stable", version=1)
    cmd_bookmark_add(args)
    out = capsys.readouterr().out
    assert "stable" in out
    assert "1" in out


def test_cmd_bookmark_add_defaults_to_latest(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    push(vault_dir, env_file)
    args = make_args(vault_dir, name="tip", version=None)
    cmd_bookmark_add(args)
    assert load_bookmarks(vault_dir)["tip"] == 2


def test_cmd_bookmark_list_empty(vault_dir, capsys):
    args = make_args(vault_dir)
    cmd_bookmark_list(args)
    out = capsys.readouterr().out
    assert "No bookmarks" in out


def test_cmd_bookmark_list_shows_entries(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    add_bookmark(vault_dir, "release", 1)
    args = make_args(vault_dir)
    cmd_bookmark_list(args)
    out = capsys.readouterr().out
    assert "release" in out
    assert "1" in out


def test_cmd_bookmark_remove_prints_confirmation(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    add_bookmark(vault_dir, "old", 1)
    args = make_args(vault_dir, name="old")
    cmd_bookmark_remove(args)
    out = capsys.readouterr().out
    assert "removed" in out.lower()


def test_cmd_bookmark_resolve_prints_version(vault_dir, env_file, capsys):
    push(vault_dir, env_file)
    add_bookmark(vault_dir, "prod", 1)
    args = make_args(vault_dir, name="prod")
    cmd_bookmark_resolve(args)
    out = capsys.readouterr().out
    assert "1" in out


def test_cmd_bookmark_resolve_missing_prints_message(vault_dir, capsys):
    args = make_args(vault_dir, name="ghost")
    cmd_bookmark_resolve(args)
    out = capsys.readouterr().out
    assert "not found" in out.lower()
