"""Tests for envault.commands_watermark command handlers."""

import sys
import types
import pytest

from envault.vault import init_vault
from envault.env_watermark import stamp
from envault.commands_watermark import (
    cmd_watermark_stamp,
    cmd_watermark_verify,
    cmd_watermark_show,
    cmd_watermark_list,
    cmd_watermark_remove,
)


@pytest.fixture
def vault_dir(tmp_path):
    d = str(tmp_path / ".vault")
    init_vault(d)
    return d


def make_args(vault_dir, **kwargs):
    ns = types.SimpleNamespace(vault_dir=vault_dir, version=None, note="", **kwargs)
    return ns


def test_cmd_watermark_stamp_prints_info(vault_dir, capsys):
    # Inject a version into manifest so _latest_version works
    from envault.vault import load_manifest, save_manifest
    m = load_manifest(vault_dir)
    m["versions"] = [1]
    save_manifest(vault_dir, m)

    args = make_args(vault_dir, author="alice", secret="s3cr3t", version=1)
    cmd_watermark_stamp(args)
    out = capsys.readouterr().out
    assert "Watermark stamped" in out
    assert "alice" in out


def test_cmd_watermark_verify_valid(vault_dir, capsys):
    stamp(vault_dir, version=1, author="bob", secret="topsecret")
    args = make_args(vault_dir, author="bob", secret="topsecret", version=1)
    cmd_watermark_verify(args)
    out = capsys.readouterr().out
    assert "VALID" in out


def test_cmd_watermark_verify_invalid_exits(vault_dir):
    stamp(vault_dir, version=1, author="carol", secret="correct")
    args = make_args(vault_dir, author="carol", secret="wrong", version=1)
    with pytest.raises(SystemExit) as exc_info:
        cmd_watermark_verify(args)
    assert exc_info.value.code == 1


def test_cmd_watermark_show_entry(vault_dir, capsys):
    stamp(vault_dir, version=2, author="dave", secret="s", note="hotfix")
    args = make_args(vault_dir, version=2)
    cmd_watermark_show(args)
    out = capsys.readouterr().out
    assert "dave" in out
    assert "hotfix" in out


def test_cmd_watermark_show_missing(vault_dir, capsys):
    args = make_args(vault_dir, version=99)
    cmd_watermark_show(args)
    out = capsys.readouterr().out
    assert "No watermark" in out


def test_cmd_watermark_list_empty(vault_dir, capsys):
    args = make_args(vault_dir)
    cmd_watermark_list(args)
    out = capsys.readouterr().out
    assert "No watermarks" in out


def test_cmd_watermark_list_shows_entries(vault_dir, capsys):
    stamp(vault_dir, version=1, author="alice", secret="s")
    stamp(vault_dir, version=2, author="bob", secret="s")
    args = make_args(vault_dir)
    cmd_watermark_list(args)
    out = capsys.readouterr().out
    assert "alice" in out
    assert "bob" in out


def test_cmd_watermark_remove_existing(vault_dir, capsys):
    stamp(vault_dir, version=1, author="x", secret="s")
    args = make_args(vault_dir, version=1)
    cmd_watermark_remove(args)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_watermark_remove_missing(vault_dir, capsys):
    args = make_args(vault_dir, version=55)
    cmd_watermark_remove(args)
    out = capsys.readouterr().out
    assert "No watermark" in out
