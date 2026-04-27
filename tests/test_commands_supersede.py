"""Tests for envault.commands_supersede."""
from __future__ import annotations

import types

import pytest

from envault.commands_supersede import (
    cmd_supersede_list,
    cmd_supersede_mark,
    cmd_supersede_show,
    cmd_supersede_unmark,
)
from envault.vault import init_vault


@pytest.fixture()
def vault_dir(tmp_path):
    d = str(tmp_path / "vault")
    init_vault(d)
    return d


def make_args(vault_dir, **kwargs):
    ns = types.SimpleNamespace(vault_dir=vault_dir, **kwargs)
    return ns


def test_cmd_supersede_mark_prints_confirmation(vault_dir, capsys):
    args = make_args(vault_dir, version=1, superseded_by=2)
    cmd_supersede_mark(args)
    out = capsys.readouterr().out
    assert "superseded by 2" in out


def test_cmd_supersede_mark_self_exits(vault_dir):
    args = make_args(vault_dir, version=3, superseded_by=3)
    with pytest.raises(SystemExit):
        cmd_supersede_mark(args)


def test_cmd_supersede_unmark_prints_confirmation(vault_dir, capsys):
    args_mark = make_args(vault_dir, version=1, superseded_by=2)
    cmd_supersede_mark(args_mark)
    args_unmark = make_args(vault_dir, version=1)
    cmd_supersede_unmark(args_unmark)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_supersede_show_no_record(vault_dir, capsys):
    args = make_args(vault_dir, version=99)
    cmd_supersede_show(args)
    out = capsys.readouterr().out
    assert "no supersede record" in out


def test_cmd_supersede_show_with_record(vault_dir, capsys):
    cmd_supersede_mark(make_args(vault_dir, version=2, superseded_by=3))
    cmd_supersede_show(make_args(vault_dir, version=2))
    out = capsys.readouterr().out
    assert "superseded by version 3" in out


def test_cmd_supersede_list_empty(vault_dir, capsys):
    cmd_supersede_list(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "No supersede records" in out


def test_cmd_supersede_list_shows_entries(vault_dir, capsys):
    cmd_supersede_mark(make_args(vault_dir, version=1, superseded_by=2))
    cmd_supersede_mark(make_args(vault_dir, version=3, superseded_by=4))
    cmd_supersede_list(make_args(vault_dir))
    out = capsys.readouterr().out
    assert "v1 -> v2" in out
    assert "v3 -> v4" in out
