"""Tests for envault/commands_deprecate.py"""

from __future__ import annotations

import argparse

import pytest

from envault.commands_deprecate import (
    cmd_deprecate_add,
    cmd_deprecate_list,
    cmd_deprecate_remove,
)
from envault.env_deprecate import deprecate_key, list_deprecated
from envault.vault import init_vault


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path))
    return str(tmp_path)


def make_args(vault_dir, **kwargs):
    ns = argparse.Namespace(vault_dir=vault_dir, **kwargs)
    return ns


def test_cmd_deprecate_add_prints_confirmation(vault_dir, capsys):
    args = make_args(vault_dir, key="OLD_TOKEN", reason="Use TOKEN_V2", replacement="TOKEN_V2")
    cmd_deprecate_add(args)
    out = capsys.readouterr().out
    assert "OLD_TOKEN" in out
    assert "deprecated" in out.lower()


def test_cmd_deprecate_add_stores_key(vault_dir, capsys):
    args = make_args(vault_dir, key="LEGACY_URL", reason="", replacement=None)
    cmd_deprecate_add(args)
    assert "LEGACY_URL" in list_deprecated(vault_dir)


def test_cmd_deprecate_add_empty_key_prints_error(vault_dir, capsys):
    args = make_args(vault_dir, key="", reason="", replacement=None)
    cmd_deprecate_add(args)
    out = capsys.readouterr().out
    assert "error" in out.lower()


def test_cmd_deprecate_remove_prints_confirmation(vault_dir, capsys):
    deprecate_key(vault_dir, "TO_REMOVE")
    args = make_args(vault_dir, key="TO_REMOVE")
    cmd_deprecate_remove(args)
    out = capsys.readouterr().out
    assert "TO_REMOVE" in out
    assert "TO_REMOVE" not in list_deprecated(vault_dir)


def test_cmd_deprecate_list_empty(vault_dir, capsys):
    args = make_args(vault_dir)
    cmd_deprecate_list(args)
    out = capsys.readouterr().out
    assert "no deprecated" in out.lower()


def test_cmd_deprecate_list_shows_keys(vault_dir, capsys):
    deprecate_key(vault_dir, "ALPHA", reason="Old", replacement="BETA")
    args = make_args(vault_dir)
    cmd_deprecate_list(args)
    out = capsys.readouterr().out
    assert "ALPHA" in out
    assert "BETA" in out
