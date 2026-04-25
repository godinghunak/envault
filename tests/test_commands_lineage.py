"""Tests for envault.commands_lineage."""

import argparse
import pytest

from envault.vault import init_vault
from envault.env_lineage import record_version
from envault.commands_lineage import (
    cmd_lineage_ancestors,
    cmd_lineage_chain,
    cmd_lineage_descendants,
    cmd_lineage_record,
    cmd_lineage_show,
)


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path)
    init_vault(d)
    return d


def make_args(vault_dir, **kwargs):
    ns = argparse.Namespace(vault_dir=vault_dir, **kwargs)
    return ns


def test_cmd_lineage_record_root(vault_dir, capsys):
    args = make_args(vault_dir, version=1, parent=None)
    cmd_lineage_record(args)
    out = capsys.readouterr().out
    assert "root" in out


def test_cmd_lineage_record_with_parent(vault_dir, capsys):
    args = make_args(vault_dir, version=2, parent=1)
    cmd_lineage_record(args)
    out = capsys.readouterr().out
    assert "parent: 1" in out


def test_cmd_lineage_ancestors_no_ancestors(vault_dir, capsys):
    record_version(vault_dir, 1, parent=None)
    args = make_args(vault_dir, version=1)
    cmd_lineage_ancestors(args)
    out = capsys.readouterr().out
    assert "no recorded ancestors" in out


def test_cmd_lineage_ancestors_shows_chain(vault_dir, capsys):
    record_version(vault_dir, 1, parent=None)
    record_version(vault_dir, 2, parent=1)
    args = make_args(vault_dir, version=2)
    cmd_lineage_ancestors(args)
    out = capsys.readouterr().out
    assert "1" in out


def test_cmd_lineage_descendants_empty(vault_dir, capsys):
    record_version(vault_dir, 1, parent=None)
    args = make_args(vault_dir, version=1)
    cmd_lineage_descendants(args)
    out = capsys.readouterr().out
    assert "no recorded descendants" in out


def test_cmd_lineage_descendants_shows_children(vault_dir, capsys):
    record_version(vault_dir, 1, parent=None)
    record_version(vault_dir, 2, parent=1)
    args = make_args(vault_dir, version=1)
    cmd_lineage_descendants(args)
    out = capsys.readouterr().out
    assert "2" in out


def test_cmd_lineage_chain_output(vault_dir, capsys):
    record_version(vault_dir, 1, parent=None)
    record_version(vault_dir, 2, parent=1)
    record_version(vault_dir, 3, parent=2)
    args = make_args(vault_dir, version=3)
    cmd_lineage_chain(args)
    out = capsys.readouterr().out
    assert "1" in out and "2" in out and "3" in out
    assert "->" in out


def test_cmd_lineage_show_empty(vault_dir, capsys):
    args = make_args(vault_dir)
    cmd_lineage_show(args)
    out = capsys.readouterr().out
    assert "No lineage" in out


def test_cmd_lineage_show_lists_versions(vault_dir, capsys):
    record_version(vault_dir, 1, parent=None)
    record_version(vault_dir, 2, parent=1)
    args = make_args(vault_dir)
    cmd_lineage_show(args)
    out = capsys.readouterr().out
    assert "v1" in out
    assert "v2" in out
