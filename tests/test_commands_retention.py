"""Tests for envault.commands_retention."""
from __future__ import annotations

import types

import pytest

from envault.commands_retention import (
    cmd_retention_apply,
    cmd_retention_clear,
    cmd_retention_set,
    cmd_retention_show,
)
from envault.env_retention import set_policy
from envault.vault import init_vault
from envault.commands import cmd_push


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("KEY=value\nOTHER=123\n")
    return str(p)


def make_args(vault_dir, **kwargs):
    args = types.SimpleNamespace(vault_dir=vault_dir, password="secret", **kwargs)
    return args


def push(vault_dir, env_file):
    args = make_args(vault_dir, env_file=env_file)
    cmd_push(args)


def test_cmd_retention_set_prints_confirmation(vault_dir, capsys):
    args = make_args(vault_dir, max_versions=5, min_keep=2)
    cmd_retention_set(args)
    out = capsys.readouterr().out
    assert "max_versions=5" in out
    assert "min_keep=2" in out


def test_cmd_retention_set_invalid_exits(vault_dir):
    args = make_args(vault_dir, max_versions=0, min_keep=1)
    with pytest.raises(SystemExit):
        cmd_retention_set(args)


def test_cmd_retention_show_no_policy(vault_dir, capsys):
    args = make_args(vault_dir)
    cmd_retention_show(args)
    out = capsys.readouterr().out
    assert "No retention policy" in out


def test_cmd_retention_show_with_policy(vault_dir, capsys):
    set_policy(vault_dir, max_versions=7, min_keep=3)
    args = make_args(vault_dir)
    cmd_retention_show(args)
    out = capsys.readouterr().out
    assert "7" in out
    assert "3" in out


def test_cmd_retention_clear_prints_confirmation(vault_dir, capsys):
    set_policy(vault_dir, max_versions=4)
    args = make_args(vault_dir)
    cmd_retention_clear(args)
    out = capsys.readouterr().out
    assert "cleared" in out.lower()


def test_cmd_retention_apply_no_versions(vault_dir, capsys):
    set_policy(vault_dir, max_versions=3, min_keep=1)
    args = make_args(vault_dir)
    cmd_retention_apply(args)
    out = capsys.readouterr().out
    assert "Nothing to prune" in out


def test_cmd_retention_apply_shows_prune_list(vault_dir, env_file, capsys):
    for _ in range(4):
        push(vault_dir, env_file)
    set_policy(vault_dir, max_versions=2, min_keep=1)
    args = make_args(vault_dir)
    cmd_retention_apply(args)
    out = capsys.readouterr().out
    assert "prune" in out.lower()
