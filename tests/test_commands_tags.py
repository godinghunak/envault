"""Tests for envault/commands_tags.py"""

import pytest
import types
from envault.vault import init_vault, load_manifest, save_manifest
from envault.tags import add_tag
from envault.commands_tags import cmd_tag_add, cmd_tag_remove, cmd_tag_list, cmd_tag_resolve


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path)
    init_vault(d)
    manifest = load_manifest(d)
    manifest["versions"] = [{"version": 1, "file": "v1.enc"}, {"version": 2, "file": "v2.enc"}]
    save_manifest(d, manifest)
    return d


def make_args(vault_dir, **kwargs):
    args = types.SimpleNamespace(vault_dir=vault_dir, version=None, **kwargs)
    return args


def test_cmd_tag_add_latest(vault_dir, capsys):
    args = make_args(vault_dir, tag="prod")
    cmd_tag_add(args)
    out = capsys.readouterr().out
    assert "Tagged version 2 as 'prod'" in out


def test_cmd_tag_add_specific_version(vault_dir, capsys):
    args = make_args(vault_dir, tag="v1", version=1)
    cmd_tag_add(args)
    out = capsys.readouterr().out
    assert "Tagged version 1 as 'v1'" in out


def test_cmd_tag_add_invalid_version(vault_dir, capsys):
    args = make_args(vault_dir, tag="bad", version=99)
    cmd_tag_add(args)
    out = capsys.readouterr().out
    assert "does not exist" in out


def test_cmd_tag_list(vault_dir, capsys):
    add_tag(vault_dir, "alpha", 1)
    add_tag(vault_dir, "beta", 2)
    args = make_args(vault_dir)
    cmd_tag_list(args)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_cmd_tag_remove(vault_dir, capsys):
    add_tag(vault_dir, "old", 1)
    args = make_args(vault_dir, tag="old")
    cmd_tag_remove(args)
    out = capsys.readouterr().out
    assert "Removed tag 'old'" in out


def test_cmd_tag_resolve(vault_dir, capsys):
    add_tag(vault_dir, "stable", 2)
    args = make_args(vault_dir, tag="stable")
    cmd_tag_resolve(args)
    out = capsys.readouterr().out
    assert "version 2" in out
